#!/usr/bin/env python3
"""Build a pixel-faithful vs. temporal RealBasicVSR FM8 portrait comparison.

The temporal network definitions are a minimal inference-only adaptation of
OpenMMLab's RealBasicVSR/BasicVSR implementation (Apache-2.0).  Keeping the
inference code here avoids installing the full MMagic training stack.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import torch
import torch.nn as nn
import torch.nn.functional as F


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def flow_warp(
    x: torch.Tensor,
    flow: torch.Tensor,
    interpolation: str = "bilinear",
    padding_mode: str = "zeros",
    align_corners: bool = True,
) -> torch.Tensor:
    if x.shape[-2:] != flow.shape[1:3]:
        raise ValueError(f"Input {x.shape[-2:]} and flow {flow.shape[1:3]} differ")
    _, _, height, width = x.shape
    grid_y, grid_x = torch.meshgrid(
        torch.arange(height, device=flow.device, dtype=x.dtype),
        torch.arange(width, device=flow.device, dtype=x.dtype),
        indexing="ij",
    )
    grid = torch.stack((grid_x, grid_y), dim=2)
    grid_flow = grid + flow
    grid_flow_x = 2.0 * grid_flow[..., 0] / max(width - 1, 1) - 1.0
    grid_flow_y = 2.0 * grid_flow[..., 1] / max(height - 1, 1) - 1.0
    grid_flow = torch.stack((grid_flow_x, grid_flow_y), dim=3)
    return F.grid_sample(
        x,
        grid_flow,
        mode=interpolation,
        padding_mode=padding_mode,
        align_corners=align_corners,
    )


class ConvModule(nn.Module):
    """The subset of mmcv.cnn.ConvModule used by the trained SPyNet."""

    def __init__(self, in_channels: int, out_channels: int, activate: bool = True):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, 7, 1, 3, bias=True)
        self.activate = nn.ReLU(inplace=True) if activate else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        return self.activate(x) if self.activate is not None else x


class SPyNetBasicModule(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.basic_module = nn.Sequential(
            ConvModule(8, 32),
            ConvModule(32, 64),
            ConvModule(64, 32),
            ConvModule(32, 16),
            ConvModule(16, 2, activate=False),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.basic_module(x)


class SPyNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.basic_module = nn.ModuleList([SPyNetBasicModule() for _ in range(6)])
        self.register_buffer("mean", torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer("std", torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))

    def compute_flow(self, ref: torch.Tensor, supp: torch.Tensor) -> torch.Tensor:
        n, _, height, width = ref.shape
        ref_pyramid = [(ref - self.mean) / self.std]
        supp_pyramid = [(supp - self.mean) / self.std]
        for _ in range(5):
            ref_pyramid.append(F.avg_pool2d(ref_pyramid[-1], 2, 2, count_include_pad=False))
            supp_pyramid.append(F.avg_pool2d(supp_pyramid[-1], 2, 2, count_include_pad=False))
        ref_pyramid.reverse()
        supp_pyramid.reverse()

        flow = ref.new_zeros(n, 2, height // 32, width // 32)
        for level, (ref_level, supp_level) in enumerate(zip(ref_pyramid, supp_pyramid)):
            if level == 0:
                flow_up = flow
            else:
                flow_up = F.interpolate(
                    flow, scale_factor=2, mode="bilinear", align_corners=True
                ) * 2.0
            warped = flow_warp(
                supp_level,
                flow_up.permute(0, 2, 3, 1),
                padding_mode="border",
            )
            flow = flow_up + self.basic_module[level](
                torch.cat((ref_level, warped, flow_up), dim=1)
            )
        return flow

    def forward(self, ref: torch.Tensor, supp: torch.Tensor) -> torch.Tensor:
        height, width = ref.shape[2:4]
        width_up = width if width % 32 == 0 else 32 * (width // 32 + 1)
        height_up = height if height % 32 == 0 else 32 * (height // 32 + 1)
        ref_up = F.interpolate(ref, size=(height_up, width_up), mode="bilinear", align_corners=False)
        supp_up = F.interpolate(supp, size=(height_up, width_up), mode="bilinear", align_corners=False)
        flow = F.interpolate(
            self.compute_flow(ref_up, supp_up),
            size=(height, width),
            mode="bilinear",
            align_corners=False,
        )
        flow[:, 0] *= width / width_up
        flow[:, 1] *= height / height_up
        return flow


class ResidualBlockNoBN(nn.Module):
    def __init__(self, mid_channels: int = 64) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(mid_channels, mid_channels, 3, 1, 1, bias=True)
        self.conv2 = nn.Conv2d(mid_channels, mid_channels, 3, 1, 1, bias=True)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.conv2(self.relu(self.conv1(x)))


class ResidualBlocksWithInputConv(nn.Module):
    def __init__(self, in_channels: int, out_channels: int = 64, num_blocks: int = 30):
        super().__init__()
        self.main = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=True),
            nn.LeakyReLU(negative_slope=0.1, inplace=True),
            nn.Sequential(*[ResidualBlockNoBN(out_channels) for _ in range(num_blocks)]),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.main(x)


class PixelShufflePack(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, scale_factor: int):
        super().__init__()
        self.scale_factor = scale_factor
        self.upsample_conv = nn.Conv2d(
            in_channels,
            out_channels * scale_factor * scale_factor,
            3,
            padding=1,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.pixel_shuffle(self.upsample_conv(x), self.scale_factor)


class BasicVSRNet(nn.Module):
    def __init__(self, mid_channels: int = 64, num_blocks: int = 20):
        super().__init__()
        self.mid_channels = mid_channels
        self.spynet = SPyNet()
        self.backward_resblocks = ResidualBlocksWithInputConv(
            mid_channels + 3, mid_channels, num_blocks
        )
        self.forward_resblocks = ResidualBlocksWithInputConv(
            mid_channels + 3, mid_channels, num_blocks
        )
        self.fusion = nn.Conv2d(mid_channels * 2, mid_channels, 1, 1, 0, bias=True)
        self.upsample1 = PixelShufflePack(mid_channels, mid_channels, 2)
        self.upsample2 = PixelShufflePack(mid_channels, 64, 2)
        self.conv_hr = nn.Conv2d(64, 64, 3, 1, 1)
        self.conv_last = nn.Conv2d(64, 3, 3, 1, 1)
        self.img_upsample = nn.Upsample(scale_factor=4, mode="bilinear", align_corners=False)
        self.lrelu = nn.LeakyReLU(negative_slope=0.1, inplace=True)

    @staticmethod
    def is_mirror_extended(lrs: torch.Tensor) -> bool:
        if lrs.shape[1] % 2:
            return False
        first, second = torch.chunk(lrs, 2, dim=1)
        return bool(torch.norm(first - second.flip(1)) == 0)

    def compute_flow(self, lrs: torch.Tensor) -> tuple[torch.Tensor | None, torch.Tensor]:
        n, t, channels, height, width = lrs.shape
        lrs_1 = lrs[:, :-1].reshape(-1, channels, height, width)
        lrs_2 = lrs[:, 1:].reshape(-1, channels, height, width)
        backward = self.spynet(lrs_1, lrs_2).view(n, t - 1, 2, height, width)
        forward = None if self.is_mirror_extended(lrs) else self.spynet(lrs_2, lrs_1).view(
            n, t - 1, 2, height, width
        )
        return forward, backward

    def forward(self, lrs: torch.Tensor) -> torch.Tensor:
        n, t, _, height, width = lrs.shape
        flows_forward, flows_backward = self.compute_flow(lrs)

        outputs: list[torch.Tensor] = []
        feat_prop = lrs.new_zeros(n, self.mid_channels, height, width)
        for index in range(t - 1, -1, -1):
            if index < t - 1:
                feat_prop = flow_warp(
                    feat_prop, flows_backward[:, index].permute(0, 2, 3, 1)
                )
            feat_prop = self.backward_resblocks(torch.cat((lrs[:, index], feat_prop), dim=1))
            outputs.append(feat_prop)
        outputs.reverse()

        feat_prop = torch.zeros_like(feat_prop)
        for index in range(t):
            current = lrs[:, index]
            if index > 0:
                flow = (
                    flows_forward[:, index - 1]
                    if flows_forward is not None
                    else flows_backward[:, -index]
                )
                feat_prop = flow_warp(feat_prop, flow.permute(0, 2, 3, 1))
            feat_prop = self.forward_resblocks(torch.cat((current, feat_prop), dim=1))
            out = self.lrelu(self.fusion(torch.cat((outputs[index], feat_prop), dim=1)))
            out = self.lrelu(self.upsample1(out))
            out = self.lrelu(self.upsample2(out))
            out = self.lrelu(self.conv_hr(out))
            outputs[index] = self.conv_last(out) + self.img_upsample(current)
        return torch.stack(outputs, dim=1)


class RealBasicVSRNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.image_cleaning = nn.Sequential(
            ResidualBlocksWithInputConv(3, 64, 20),
            nn.Conv2d(64, 3, 3, 1, 1, bias=True),
        )
        self.basicvsr = BasicVSRNet(64, 20)
        self.basicvsr.spynet.requires_grad_(False)

    def forward(self, lqs: torch.Tensor) -> torch.Tensor:
        lqs = lqs.clone()
        _, frame_count, _, _, _ = lqs.shape
        # Sequential cleaning lowers peak memory without altering the result.
        for _ in range(3):
            residues = []
            for index in range(frame_count):
                residue = self.image_cleaning(lqs[:, index])
                lqs[:, index] = lqs[:, index] + residue
                residues.append(residue)
            residue_stack = torch.stack(residues, dim=1)
            if torch.mean(torch.abs(residue_stack)) < (255.0 / 255.0):
                break
        return self.basicvsr(lqs)


def load_frames(input_dir: Path) -> tuple[list[Path], list[Image.Image], np.ndarray]:
    paths = sorted(input_dir.glob("frame_*.bmp"))
    if not paths:
        paths = sorted(input_dir.glob("frame_*.png"))
    if not paths:
        raise FileNotFoundError(f"No frame_*.bmp or frame_*.png files in {input_dir}")
    images = [Image.open(path).convert("RGB") for path in paths]
    dimensions = {image.size for image in images}
    if len(dimensions) != 1:
        raise ValueError(f"Mixed frame dimensions: {sorted(dimensions)}")
    rgb = np.stack([np.asarray(image, dtype=np.uint8) for image in images])
    return paths, images, rgb


def save_deterministic(images: list[Image.Image], output_dir: Path) -> np.ndarray:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, image in enumerate(images, 1):
        restored = image.resize((image.width * 4, image.height * 4), Image.Resampling.LANCZOS)
        restored = restored.filter(ImageFilter.UnsharpMask(radius=1.0, percent=65, threshold=3))
        restored.save(output_dir / f"frame_{index:04d}.png", optimize=True)
        frames.append(np.asarray(restored, dtype=np.uint8))
    return np.stack(frames)


def load_realbasicvsr(checkpoint_path: Path, device: torch.device) -> RealBasicVSRNet:
    model = RealBasicVSRNet()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    state = checkpoint["state_dict"]
    prefix = "generator_ema."
    weights = {key[len(prefix):]: value for key, value in state.items() if key.startswith(prefix)}
    missing, unexpected = model.load_state_dict(weights, strict=False)
    if missing or unexpected:
        raise RuntimeError(f"Checkpoint mismatch; missing={missing}, unexpected={unexpected}")
    model.eval().requires_grad_(False)
    return model.to(device)


def save_temporal(
    source_rgb: np.ndarray,
    checkpoint_path: Path,
    output_dir: Path,
    device: torch.device,
) -> np.ndarray:
    output_dir.mkdir(parents=True, exist_ok=True)
    model = load_realbasicvsr(checkpoint_path, device)
    tensor = torch.from_numpy(source_rgb.astype(np.float32) / 255.0)
    tensor = tensor.permute(0, 3, 1, 2).unsqueeze(0).to(device)
    with torch.inference_mode():
        restored = model(tensor).clamp_(0.0, 1.0)
    restored = (
        restored.squeeze(0).permute(0, 2, 3, 1).mul(255.0).round().byte().cpu().numpy()
    )
    for index, frame in enumerate(restored, 1):
        Image.fromarray(frame, "RGB").save(
            output_dir / f"frame_{index:04d}.png", optimize=True
        )
    del model, tensor
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return restored


def downscale_frames(frames: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    return np.stack(
        [
            np.asarray(Image.fromarray(frame).resize(size, Image.Resampling.LANCZOS), dtype=np.uint8)
            for frame in frames
        ]
    )


def gradient_energy(frames: np.ndarray) -> float:
    values = frames.astype(np.float32)
    dx = np.abs(values[:, :, 1:] - values[:, :, :-1]).mean()
    dy = np.abs(values[:, 1:] - values[:, :-1]).mean()
    return float((dx + dy) / 2.0)


def evaluate(source: np.ndarray, output: np.ndarray) -> dict[str, float]:
    source_float = source.astype(np.float32)
    down = downscale_frames(output, (source.shape[2], source.shape[1])).astype(np.float32)
    error = down - source_float
    mse = float(np.mean(error * error))
    psnr = 99.0 if mse == 0 else 10.0 * math.log10((255.0 * 255.0) / mse)
    source_delta = np.abs(np.diff(source_float, axis=0))
    output_delta = np.abs(np.diff(down, axis=0))
    source_motion = float(source_delta.mean())
    output_motion = float(output_delta.mean())
    static_mask = np.max(source_delta, axis=3) <= 1.0
    static_output = np.mean(output_delta, axis=3)[static_mask]
    return {
        "roundtrip_psnr_db": round(psnr, 5),
        "roundtrip_mae": round(float(np.abs(error).mean()), 5),
        "source_adjacent_delta": round(source_motion, 5),
        "output_adjacent_delta_after_downscale": round(output_motion, 5),
        "temporal_delta_ratio": round(output_motion / max(source_motion, 1e-9), 5),
        "static_region_flicker": round(float(static_output.mean()) if static_output.size else 0.0, 5),
        "detail_gradient_energy_4x": round(gradient_energy(output), 5),
    }


def font(size: int) -> ImageFont.ImageFont:
    candidates = (
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def labelled_comparison_frame(
    source: np.ndarray,
    deterministic: np.ndarray,
    temporal: np.ndarray,
    frame_number: int,
) -> Image.Image:
    original = Image.fromarray(source).resize((480, 400), Image.Resampling.NEAREST)
    left = Image.fromarray(deterministic)
    right = Image.fromarray(temporal)
    canvas = Image.new("RGB", (1440, 448), "black")
    canvas.paste(original, (0, 48))
    canvas.paste(left, (480, 48))
    canvas.paste(right, (960, 48))
    draw = ImageDraw.Draw(canvas)
    label_font = font(22)
    labels = ("ORIGINAL (4x nearest)", "DETERMINISTIC", "TEMPORAL RealBasicVSR")
    for column, label in enumerate(labels):
        box = draw.textbbox((0, 0), label, font=label_font)
        label_width = box[2] - box[0]
        draw.text(
            (column * 480 + (480 - label_width) // 2, 11),
            label,
            fill=(235, 235, 235),
            font=label_font,
        )
    draw.text((1370, 414), f"{frame_number:04d}", fill=(180, 180, 180), font=font(14))
    return canvas


def create_comparisons(
    source: np.ndarray,
    deterministic: np.ndarray,
    temporal: np.ndarray,
    output_root: Path,
) -> None:
    preview_frames = output_root / "comparison_frames"
    preview_frames.mkdir(parents=True, exist_ok=True)
    for index in range(len(source)):
        labelled_comparison_frame(
            source[index], deterministic[index], temporal[index], index + 1
        ).save(preview_frames / f"frame_{index + 1:04d}.png", optimize=True)

    chosen = np.linspace(0, len(source) - 1, 6, dtype=int)
    sheet = Image.new("RGB", (1440, 448 * len(chosen)), "black")
    for row, index in enumerate(chosen):
        sheet.paste(
            labelled_comparison_frame(source[index], deterministic[index], temporal[index], index + 1),
            (0, row * 448),
        )
    sheet.save(output_root / "contact_sheet.png", optimize=True)


def run_ffmpeg(command: list[str]) -> None:
    subprocess.run(command, check=True)


def encode_previews(output_root: Path, fps: float) -> None:
    common = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    run_ffmpeg(
        common
        + [
            "-framerate",
            str(fps),
            "-i",
            str(output_root / "comparison_frames/frame_%04d.png"),
            "-c:v",
            "libx264",
            "-crf",
            "15",
            "-pix_fmt",
            "yuv420p",
            str(output_root / "comparison.mp4"),
        ]
    )
    for directory, filename in (
        ("deterministic_frames", "deterministic.mp4"),
        ("temporal_frames", "temporal_realbasicvsr.mp4"),
    ):
        run_ffmpeg(
            common
            + [
                "-framerate",
                str(fps),
                "-i",
                str(output_root / directory / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-crf",
                "15",
                "-pix_fmt",
                "yuv420p",
                str(output_root / filename),
            ]
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--fps", type=float, default=12.5)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    started = time.time()
    paths, images, source = load_frames(args.input_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    deterministic = save_deterministic(images, args.output_dir / "deterministic_frames")

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available")
    device = torch.device(args.device)
    temporal = save_temporal(
        source, args.checkpoint, args.output_dir / "temporal_frames", device
    )
    if deterministic.shape != temporal.shape:
        raise RuntimeError(
            f"Branch shape mismatch: deterministic={deterministic.shape}, temporal={temporal.shape}"
        )

    metrics = {
        "clip": args.input_dir.name,
        "source_frames": len(paths),
        "source_dimensions": [int(source.shape[2]), int(source.shape[1])],
        "output_dimensions": [int(temporal.shape[2]), int(temporal.shape[1])],
        "comparison_fps_provisional": args.fps,
        "frame_interpolation": False,
        "deterministic": evaluate(source, deterministic),
        "temporal_realbasicvsr": evaluate(source, temporal),
        "checkpoint": {
            "filename": args.checkpoint.name,
            "sha256": sha256_file(args.checkpoint),
            "source": "OpenMMLab RealBasicVSR GAN x4 pretrained checkpoint",
        },
        "input_frame_hashes": {path.name: sha256_file(path) for path in paths},
        "elapsed_seconds": round(time.time() - started, 3),
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    create_comparisons(source, deterministic, temporal, args.output_dir)
    encode_previews(args.output_dir, args.fps)
    metrics["elapsed_seconds"] = round(time.time() - started, 3)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
