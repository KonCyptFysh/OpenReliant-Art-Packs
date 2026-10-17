// SPDX-License-Identifier: MPL-2.0
// Material/light composition adapted from OpenReliant 0.18.0 device.glsl.
// See LICENSE-OpenReliant.txt. Local surface spill; does not cast onto other objects.
// Native mesh parts use separate shader frames. Exact plane/normal masks prevent
// engine coordinates selecting similar locations on the hull or support arms.
vec3 pr18_compose(vec3 texel, Lit material, vec3 added, vec3 highlights) {
    vec3 diffuse = texel * (1.0 - material.metallic);
    if (frame.settings.w > 0.0) {
        return min(encoded(diffuse * min(added, vec3(1.0)) + highlights)
            + encoded(texel) * color.rgb * material.ambient, vec3(1.0));
    }
    if (!material.material) return texel * min(color.rgb * material.ambient + added, vec3(1.0));
    return min(texel * color.rgb * material.ambient + diffuse * added + highlights, vec3(1.0));
}

vec3 pr18_engine_spill(Surface pixel, float drive, vec3 lightPosition, float reach) {
    vec3 delta = lightPosition - pixel.local;
    float distanceToLight = length(delta);
    if (drive <= 0.00001 || distanceToLight >= reach || distanceToLight < 0.001) return vec3(0.0);
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
    vec3 before = pr18_compose(texel, material, added, highlights);
    float falloff = pow(1.0 - distanceToLight / reach, 2.0) * drive * 1.8;
    vec3 lamp = vec3(1.0, 0.075, 0.012);
    vec3 diffuseAdd = lamp * (falloff * cosine);
    vec3 specularAdd = vec3(0.0);
    if (material.material) {
        Lit localMaterial = material;
        localMaterial.normal = localNormal;
        localMaterial.toEye = objectDirection(pixel.toEye);
        specularAdd = highlight(localMaterial, towardLight) * falloff * lamp;
    }
    return max(pr18_compose(texel, material, added + diffuseAdd, highlights + specularAdd) - before, vec3(0.0));
}

const vec4 planes0[9] = vec4[](vec4(0.0000000,0.0000000,-1.0000000,407.9062500),vec4(-0.9805960,-0.0000000,-0.1960393,288.0236780),vec4(1.0000000,-0.0000000,-0.0000002,-147.7857046),vec4(0.9805960,0.0000000,-0.1960396,300.6112895),vec4(-0.0000000,-0.9830337,-0.1834251,276.3312562),vec4(0.0000000,1.0000000,0.0000000,-144.8922729),vec4(-1.0000000,0.0000000,0.0000002,-160.6224986),vec4(-0.0000000,0.9830337,-0.1834251,274.4271684),vec4(-0.0000000,-1.0000000,0.0000002,-142.9554606));
const float hot0[9] = float[](1.0,0.0,1.0,0.0,0.0,1.0,1.0,0.0,1.0);
vec2 nozzle0(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(-217.6776428,-210.1580200,-730.4833984))) || any(greaterThan(at,vec3(230.5142517,208.2210693,-382.3830566)))) return vec2(0.0);
 vec2 weight=vec2(0.0);
 for (int j=0;j<9;j++) {
  vec4 plane=planes0[j];
  if (dot(normal,plane.xyz) > 0.99995 && abs(dot(at,plane.xyz)-plane.w) < 0.35) weight=max(weight,vec2(1.0,hot0[j]));
 }
 return weight;
}
const vec4 planes1[9] = vec4[](vec4(0.0000000,-0.0000000,-1.0000000,419.3837891),vec4(-1.0000000,0.0000000,0.0000004,-143.6327273),vec4(0.9805959,0.0000000,-0.1960399,286.2012947),vec4(0.0000000,1.0000000,0.0000000,-141.3071289),vec4(0.0000000,-0.9830337,-0.1834252,274.9122518),vec4(-0.9805960,0.0000000,-0.1960393,306.9338687),vec4(1.0000000,0.0000000,-0.0000004,-164.7754758),vec4(0.0000000,-1.0000000,0.0000002,-146.5406068),vec4(0.0000000,0.9830337,-0.1834252,280.0567987));
const float hot1[9] = float[](1.0,1.0,0.0,1.0,0.0,0.0,1.0,1.0,0.0);
vec2 nozzle1(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(-234.6674805,-206.5728760,-741.9606934))) || any(greaterThan(at,vec3(213.5244141,211.8062134,-393.8605957)))) return vec2(0.0);
 vec2 weight=vec2(0.0);
 for (int j=0;j<9;j++) {
  vec4 plane=planes1[j];
  if (dot(normal,plane.xyz) > 0.99995 && abs(dot(at,plane.xyz)-plane.w) < 0.35) weight=max(weight,vec2(1.0,hot1[j]));
 }
 return weight;
}
const vec4 planes2[21] = vec4[](vec4(-0.0000000,-0.0000000,-1.0000000,1485.0034180),vec4(0.8278240,-0.2689750,-0.4923006,845.4117795),vec4(0.5116230,-0.7041887,-0.4923009,720.3241719),vec4(-0.0000000,-0.8704251,-0.4923009,673.5560444),vec4(-0.5116232,-0.7041887,-0.4923008,722.9711150),vec4(-0.8278232,-0.2689758,-0.4923015,849.6958323),vec4(-0.8278233,0.2689760,-0.4923012,1005.3233446),vec4(-0.5116228,0.7041883,-0.4923017,1130.4117339),vec4(0.0000007,0.8704243,-0.4923023,1177.1806769),vec4(0.5116228,0.7041882,-0.4923018,1127.7647954),vec4(0.8278231,0.2689748,-0.4923022,1001.0412917),vec4(-0.9018902,0.2930407,-0.3173659,441.2522875),vec4(-0.5573984,0.7671935,-0.3173660,577.5320871),vec4(-0.0000000,0.9483033,-0.3173656,628.4840815),vec4(0.5573995,0.7671930,-0.3173653,574.6470581),vec4(0.9018901,0.2930421,-0.3173651,436.5851464),vec4(0.9018897,-0.2930423,-0.3173660,267.0339885),vec4(0.5573983,-0.7671934,-0.3173663,130.7552913),vec4(0.0000000,-0.9483034,-0.3173652,79.8006943),vec4(-0.5573991,-0.7671930,-0.3173660,133.6388473),vec4(-0.9018902,-0.2930408,-0.3173659,271.7006965));
const float hot2[21] = float[](1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0);
vec2 nozzle2(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(-237.7975159,65.5739746,-1596.2395020))) || any(greaterThan(at,vec3(232.6236572,513.0201416,-1484.5034180)))) return vec2(0.0);
 vec2 weight=vec2(0.0);
 for (int j=0;j<21;j++) {
  vec4 plane=planes2[j];
  if (dot(normal,plane.xyz) > 0.99995 && abs(dot(at,plane.xyz)-plane.w) < 0.35) weight=max(weight,vec2(1.0,hot2[j]));
 }
 return weight;
}
void surface(inout Surface s, vec4 parameters, float time) {
 s.glow *= clamp(parameters.x,0.0,1.0);
 vec3 geometric=cross(dFdx(s.local),dFdy(s.local));
 geometric/=max(length(geometric),0.000001);
 if (dot(geometric,objectDirection(facing))<0.0) geometric=-geometric;
 float drive=clamp(parameters.y,0.0,1.0),heat=clamp(parameters.z,0.0,1.0);
 float thermal=0.0;
 vec2 n0=nozzle0(s.local,geometric);
 if(n0.x>0.0) s.glow += pr18_engine_spill(s,drive,vec3(6.4180000,-0.9680000,-780.0000000),680.0);
 thermal=max(thermal,n0.y);
 vec2 n1=nozzle1(s.local,geometric);
 if(n1.x>0.0) s.glow += pr18_engine_spill(s,drive,vec3(-10.5720000,2.6170000,-791.5000000),680.0);
 thermal=max(thermal,n1.y);
 vec2 n2=nozzle2(s.local,geometric);
 if(n2.x>0.0) s.glow += pr18_engine_spill(s,drive,vec3(-2.6000000,289.3000000,-1640.0000000),580.0);
 thermal=max(thermal,n2.y);
 float detail=0.45+0.55*clamp(dot(s.color,vec3(0.2126,0.7152,0.0722))*2.0,0.0,1.0);
 s.glow+=thermal*detail*(0.16*drive+0.46*heat)*mix(vec3(0.65,0.035,0.005),vec3(1.0,0.20,0.025),heat);
 s.glow*=clamp(parameters.w,0.0,1.0);
}
