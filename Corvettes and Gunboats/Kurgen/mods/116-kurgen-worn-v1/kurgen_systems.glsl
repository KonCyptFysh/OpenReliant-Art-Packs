// SPDX-License-Identifier: MPL-2.0
// Color composition is adapted from OpenReliant v0.18.0 device.glsl.
// This file is subject to the Mozilla Public License, v. 2.0. See
// LICENSE-OpenReliant.txt or https://mozilla.org/MPL/2.0/ .
// Kurgen PoC, official OpenReliant 0.18.0 surface-function API.
// x cabin brightness, y fast engine response, z retained nozzle heat, w visibility.
// Recreates only the removed steady stern lamp's contribution on this hull. Its native
// position, color, range and full-power intensity are unchanged. No global shader override.
// Other objects no longer receive that lamp: this deliberately scoped surface effect is
// not a script-controlled scene light (0.18 exposes no such brightness setter).

vec3 ku18_compose(vec3 texel, Lit material, vec3 added, vec3 highlights) {
    vec3 diffuse = texel * (1.0 - material.metallic);
    if (frame.settings.w > 0.0) {
        return min(encoded(diffuse * min(added, vec3(1.0)) + highlights)
            + encoded(texel) * color.rgb * material.ambient, vec3(1.0));
    }
    if (!material.material) return texel * min(color.rgb * material.ambient + added, vec3(1.0));
    return min(texel * color.rgb * material.ambient + diffuse * added + highlights, vec3(1.0));
}

vec3 ku18_engine_spill(Surface pixel, float drive) {
    vec3 delta = vec3(-28.5745697, 62.7972527, -2572.3293457) - pixel.local;
    float distanceToLight = length(delta);
    if (drive <= 0.00001 || distanceToLight >= 2000.0 || distanceToLight < 0.001) return vec3(0.0);
    vec3 localNormal = objectDirection(pixel.normal);
    vec3 towardLight = delta / distanceToLight;
    float cosine = max(dot(localNormal, towardLight), 0.0);
    if (cosine <= 0.0) return vec3(0.0);

    // Use the engine's own material and lighting helpers so the broad effect retains
    // normal-map relief and moving specular reflections, rather than a red painted patch.
    mat3 onTexture = mat3(0.0);
    if ((shade & shadeNormalMap) != 0u) {
        vec3 unbent = dot(facing, facing) < 1e-12 ? vec3(0.0,0.0,1.0) : normalize(facing);
        onTexture = textureFrame(unbent, place, uv);
    }
    vec3 texel = frame.settings.w > 0.0 ? decoded(pixel.color) : pixel.color;
    Lit material = litOf(vec4(texel, pixel.alpha), onTexture);
    vec3 highlights;
    vec3 added = lights(material, highlights);
    if (material.material) highlights += surroundings(material);
    vec3 before = ku18_compose(texel, material, added, highlights);
    float falloff = pow(1.0 - distanceToLight / 2000.0, 2.0) * drive;
    vec3 lamp = vec3(1.0, 0.0, 0.0);
    vec3 diffuseAdd = lamp * (falloff * cosine);
    vec3 specularAdd = vec3(0.0);
    if (material.material) {
        Lit localMaterial = material;
        localMaterial.normal = localNormal;
        localMaterial.toEye = objectDirection(pixel.toEye);
        specularAdd = highlight(localMaterial, towardLight) * falloff * lamp;
    }
    return max(ku18_compose(texel, material, added + diffuseAdd, highlights + specularAdd) - before, vec3(0.0));
}

float ku18_nozzle(vec3 at, vec3 normal, vec3 center) {
    // Only the recessed end disk, not the exterior cowling or cylindrical side walls.
    float disk = 1.0 - smoothstep(104.0, 124.0, length(at.xy - center.xy));
    // LOD 2 flattens the same end disk 101 units farther aft. Its exterior rim remains out.
    float planeDistance = min(abs(at.z - center.z), abs(at.z - (center.z - 101.0)));
    float depth = 1.0 - smoothstep(3.0, 7.0, planeDistance);
    float facingBack = smoothstep(0.65, 0.95, -normal.z);
    return disk * depth * facingBack;
}

float ku18_nozzle_petals(vec3 at, vec3 normal, vec3 center) {
    // The native inward-sloping octagonal petals flare from radius 137 to 212
    // over 101 units aft. Select their geometry, independently of the bump map.
    vec2 radial = at.xy - center.xy;
    float radius = length(radial);
    float aft = center.z - at.z;
    float inward = smoothstep(0.12, 0.35, -dot(normal.xy, radial / max(radius, 1.0)));
    // Match the native petal slope and its simplified LOD 1 interiors. Coarse
    // LOD hull triangles can cross this volume after the nozzle is removed.
    float detailed = 1.0 - smoothstep(0.003, 0.009, abs(-normal.z - 0.5675));
    float back = max(detailed, smoothstep(0.70, 0.72, -normal.z));
    float depth = (1.0 - smoothstep(2.0, 6.0, -aft))
                * (1.0 - smoothstep(96.0, 102.5, aft));
    float inside = 1.0 - smoothstep(211.0, 215.0, radius);
    // Warmest at the recessed throat; cooler toward the lip. Exterior stays dark.
    float taper = mix(1.25, 0.75, clamp(aft / 101.0, 0.0, 1.0));
    return inward * back * depth * inside * taper;
}

void surface(inout Surface s, vec4 parameters, float time) {
    // The approved emissive maps contain bridge glass only; no vent windows are added.
    s.glow *= clamp(parameters.x, 0.0, 1.0);
    s.glow += ku18_engine_spill(s, clamp(parameters.y, 0.0, 1.0));
    vec3 n = objectDirection(s.normal);
    float nozzle = max(ku18_nozzle(s.local, n, vec3(-677.95,204.75,-2026.06)),
                       ku18_nozzle(s.local, n, vec3(617.95,202.76,-2028.05)));
    vec3 geometric = cross(dFdx(s.local), dFdy(s.local));
    geometric /= max(length(geometric), 0.000001);
    if (dot(geometric, objectDirection(facing)) < 0.0) geometric = -geometric;
    float petals = max(ku18_nozzle_petals(s.local, geometric, vec3(-677.95,204.75,-2026.06)),
                       ku18_nozzle_petals(s.local, geometric, vec3(617.95,202.76,-2028.05)));
    nozzle = max(nozzle, petals);
    float heat = clamp(parameters.z, 0.0, 1.0);
    float power = 0.12 * clamp(parameters.y, 0.0, 1.0) + 0.48 * heat;
    // Keep the existing nozzle's texture legible through its incandescence.
    float detail = 0.45 + 0.55 * clamp(dot(s.color, vec3(0.2126,0.7152,0.0722)) * 2.0, 0.0, 1.0);
    s.glow += nozzle * detail * power * mix(vec3(0.65,0.035,0.005), vec3(1.0,0.20,0.025), heat);
    s.glow *= clamp(parameters.w, 0.0, 1.0);
}
