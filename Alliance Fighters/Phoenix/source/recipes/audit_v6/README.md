# Frame-fitted glazing

This pass starts from the latest v5 scene without changing geometry, corner normals or UVs. `frame_paths.json` traces the original inside gasket edges with smooth quadratic corners, including dark areas omitted by the earlier colour threshold. Glass normals are planar through the pane and gasket. The soft transition back to the hull normal map occurs outside the gasket.

Set PHOENIX_WORKSPACE to the canonical worn directory and OPENRELIANT_SLTOOL to the official 0.7.0 validator. The build requires the recorded v5 starting scene; do not run it blindly over later manual edits. Checks cover original frame colour preservation, map locality, coverage of previously missed glass, flat normals through glass edges, and exact v5 native model hashes.
