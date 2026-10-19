// SPDX-License-Identifier: MPL-2.0
// Material/light composition adapted from OpenReliant 0.18.0 device.glsl.
// See LICENSE-OpenReliant.txt. Local surface spill; does not cast onto other objects.
// Native mesh parts use separate shader frames. Exact plane/normal masks prevent
// engine coordinates selecting similar locations on the hull or support arms.
vec3 rl18_compose(vec3 texel, Lit material, vec3 added, vec3 highlights) {
    vec3 diffuse = texel * (1.0 - material.metallic);
    if (frame.settings.w > 0.0) {
        return min(encoded(diffuse * min(added, vec3(1.0)) + highlights)
            + encoded(texel) * color.rgb * material.ambient, vec3(1.0));
    }
    if (!material.material) return texel * min(color.rgb * material.ambient + added, vec3(1.0));
    return min(texel * color.rgb * material.ambient + diffuse * added + highlights, vec3(1.0));
}

vec3 rl18_engine_spill(Surface pixel, float drive, vec3 lightPosition, float reach) {
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
    vec3 before = rl18_compose(texel, material, added, highlights);
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
    return max(rl18_compose(texel, material, added + diffuseAdd, highlights + specularAdd) - before, vec3(0.0));
}


const vec4 planes0[30] = vec4[](vec4(-0.0000202,-0.0029184,-0.9999957,-177.5227832),vec4(-0.0011961,0.0001335,-0.9999993,-177.4319060),vec4(-0.0011961,0.0011200,-0.9999987,-177.0972062),vec4(-0.0024345,-0.0022679,-0.9999945,-179.2391220),vec4(-0.0000201,0.0005896,-0.9999998,-178.8269411),vec4(-0.0000939,0.0004060,-0.9999999,-178.6819060),vec4(-0.9421262,0.0023977,-0.3352498,-814.2853491),vec4(-0.7190012,0.6075681,-0.3374881,-861.0918330),vec4(-0.0000031,0.9441980,-0.3293785,-931.3504406),vec4(0.7100709,0.6179306,-0.3375811,-1029.8489657),vec4(0.9412041,0.0052954,-0.3377971,-1043.1169503),vec4(0.6817946,-0.6495249,-0.3365614,-993.6334208),vec4(-0.0007828,-0.9483116,-0.3173397,-853.1304066),vec4(-0.6913338,-0.6395993,-0.3361106,-830.9474514),vec4(-0.0006087,-0.0005803,-0.9999996,-178.0328009),vec4(-0.0006087,-0.0002275,-0.9999998,-178.0385419),vec4(-0.6014925,0.6058674,-0.5207028,-584.1194646),vec4(-0.6209359,0.5248653,-0.5821984,-518.0044147),vec4(0.5731101,0.5871648,-0.5716489,-710.0132777),vec4(0.6464197,0.5626421,-0.5153401,-776.0946404),vec4(0.5751406,-0.6245619,-0.5283330,-684.7664512),vec4(0.5925323,-0.5644919,-0.5746776,-644.5210084),vec4(-0.5625727,-0.6016376,-0.5670486,-541.5973432),vec4(-0.6267361,-0.5798365,-0.5205684,-585.0981588),vec4(-0.6633358,-0.7094269,-0.2381158,-562.1654093),vec4(-0.5143332,0.5369268,-0.6687085,-73.9665169),vec4(0.5057745,-0.5293791,-0.6811387,-165.5709828),vec4(0.5033740,-0.5468878,-0.6689756,-171.4488140),vec4(-0.5163618,0.5199194,-0.6804809,-66.8963374),vec4(0.6779370,0.6943905,-0.2412948,-762.1689786));
float nozzle0(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(-1390.0136719,-1257.8764648,-779.7285156))) || any(greaterThan(at,vec3(1143.2910156,1160.4838867,179.2285156)))) return 0.0;
 for(int j=0;j<30;j++) {vec4 p=planes0[j];if(dot(normal,p.xyz)>.99995 && abs(dot(at,p.xyz)-p.w)<.35) return 1.0;}
 return 0.0;
}

const vec4 planes1[12] = vec4[](vec4(-0.0007127,0.0001312,-0.9999997,-1917.1832914),vec4(-0.0000651,-0.0001810,-1.0000000,-1919.4767714),vec4(-0.0000779,-0.0001810,-1.0000000,-1919.4258715),vec4(0.0001300,-0.0003023,-0.9999999,-1920.3707401),vec4(-0.8871958,-0.0048847,-0.4613672,1949.0802343),vec4(-0.2347102,0.8278013,-0.5095647,-790.6487156),vec4(0.3454987,0.8031066,-0.4854384,-3028.3189384),vec4(0.8758028,-0.0000303,-0.4826690,-5174.5052749),vec4(-0.2830254,-0.8190231,-0.4990970,-633.2811369),vec4(0.3464323,-0.8053247,-0.4810787,-3087.3709241),vec4(-0.0003152,0.0000413,-0.9999999,-1918.3911155),vec4(0.2916973,-0.6780864,-0.6746195,-2912.9179590));
float nozzle1(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(-5268.1230469,-1363.3940430,1161.6757812))) || any(greaterThan(at,vec3(-2795.0800781,1434.8862305,1920.3984375)))) return 0.0;
 for(int j=0;j<12;j++) {vec4 p=planes1[j];if(dot(normal,p.xyz)>.99995 && abs(dot(at,p.xyz)-p.w)<.35) return 1.0;}
 return 0.0;
}

const vec4 planes2[12] = vec4[](vec4(0.0066566,-0.0029406,-0.9999735,-1897.2554171),vec4(0.0007376,-0.0001811,-0.9999997,-1916.6868010),vec4(-0.0000779,-0.0001810,-1.0000000,-1919.7247029),vec4(0.0001301,-0.0003023,-0.9999999,-1918.8396328),vec4(0.8898473,-0.0045199,-0.4562360,1755.3582487),vec4(0.2394351,0.8317402,-0.5008782,-827.3880917),vec4(-0.3472960,0.8072807,-0.4771618,-2945.0241501),vec4(-0.8757212,-0.0000411,-0.4828171,-4955.2799890),vec4(0.2871132,-0.8129474,-0.5066385,-688.4808010),vec4(-0.3445773,-0.8010177,-0.4895274,-2997.0934920),vec4(0.0024781,-0.0022743,-0.9999943,-1909.1902534),vec4(-0.2967527,0.6897950,-0.6603944,-2810.2542355));
float nozzle2(vec3 at, vec3 normal) {
 if (any(lessThan(at,vec3(2562.6586914,-1363.8657227,1155.4355469))) || any(greaterThan(at,vec3(5018.1166992,1434.4135742,1920.0996094)))) return 0.0;
 for(int j=0;j<12;j++) {vec4 p=planes2[j];if(dot(normal,p.xyz)>.99995 && abs(dot(at,p.xyz)-p.w)<.35) return 1.0;}
 return 0.0;
}
void surface(inout Surface s, vec4 parameters, float time) {
 s.glow *= clamp(parameters.x,0.0,1.0);
 vec3 geometric=cross(dFdx(s.local),dFdy(s.local));
 geometric/=max(length(geometric),0.000001);
 if(dot(geometric,objectDirection(s.toEye))<0.0) geometric=-geometric;
 float drive=clamp(parameters.y,0.0,1.0),heat=clamp(parameters.z,0.0,1.0),thermal=0.0;
 float n0=nozzle0(s.local,geometric);
 if(n0>0.0) s.glow+=rl18_engine_spill(s,drive,vec3(-127.8400000,-45.2300000,-1050.0000000),3300.0);
 thermal=max(thermal,n0);
 float n1=nozzle1(s.local,geometric);
 if(n1>0.0) s.glow+=rl18_engine_spill(s,drive,vec3(-4061.5100000,-45.2300000,840.0000000),2800.0);
 thermal=max(thermal,n1);
 float n2=nozzle2(s.local,geometric);
 if(n2>0.0) s.glow+=rl18_engine_spill(s,drive,vec3(3822.7500000,-45.2300000,840.0000000),2800.0);
 thermal=max(thermal,n2);
 float detail=.45+.55*clamp(dot(s.color,vec3(.2126,.7152,.0722))*2.0,0.0,1.0);
 s.glow+=thermal*detail*(.16*drive+.46*heat)*mix(vec3(.65,.035,.005),vec3(1.0,.20,.025),heat);
 s.glow*=clamp(parameters.w,0.0,1.0);
}
