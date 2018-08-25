/*
 * Copyright 2013 Google Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <cstring>
#include "patch.h"

void UnpackPatch(const char bulk[128], char patch[156]) {
	for (int op = 0; op < 6; op++) {
		// eg rate and level, brk pt, depth, scaling
		memcpy(patch + op * 21, bulk + op * 17, 11);
		char leftrightcurves = bulk[op * 17 + 11];
		patch[op * 21 + 11] = leftrightcurves & 3;
		patch[op * 21 + 12] = (leftrightcurves >> 2) & 3;
		char detune_rs = bulk[op * 17 + 12];
		patch[op * 21 + 13] = detune_rs & 7;
		patch[op * 21 + 20] = detune_rs >> 3;
		char kvs_ams = bulk[op * 17 + 13];
		patch[op * 21 + 14] = kvs_ams & 3;
		patch[op * 21 + 15] = kvs_ams >> 2;
		patch[op * 21 + 16] = bulk[op * 17 + 14];  // output level
		char fcoarse_mode = bulk[op * 17 + 15];
		patch[op * 21 + 17] = fcoarse_mode & 1;
		patch[op * 21 + 18] = fcoarse_mode >> 1;
		patch[op * 21 + 19] = bulk[op * 17 + 16];  // fine freq
	}
	memcpy(patch + 126, bulk + 102, 9);  // pitch env, algo
	char oks_fb = bulk[111];
	patch[135] = oks_fb & 7;
	patch[136] = oks_fb >> 3;
	memcpy(patch + 137, bulk + 112, 4);  // lfo
	char lpms_lfw_lks = bulk[116];
	patch[141] = lpms_lfw_lks & 1;
	patch[142] = (lpms_lfw_lks >> 1) & 7;
	patch[143] = lpms_lfw_lks >> 4;
	memcpy(patch + 144, bulk + 117, 11);  // transpose, name
	patch[155] = 0x3f;  // operator on/off
}

char clamp(char byte, int pos, char max) {
	if(byte > max || byte < 0) {
		return max;
	}
	return byte;
}
void CheckPatch(char patch[156]) {
	int pos = 0;
	for(int op=0;op<6;op++) {
		for(int k=0;k<11;k++) {
			patch[pos] = clamp(patch[pos], pos, 99); pos++;
		}
		patch[pos] = clamp(patch[pos], pos, 3); pos++;
		patch[pos] = clamp(patch[pos], pos, 3); pos++;
		patch[pos] = clamp(patch[pos], pos, 7); pos++;
		patch[pos] = clamp(patch[pos], pos, 3); pos++;
		patch[pos] = clamp(patch[pos], pos, 7); pos++;
		patch[pos] = clamp(patch[pos], pos, 99); pos++;
		patch[pos] = clamp(patch[pos], pos, 1); pos++;
		patch[pos] = clamp(patch[pos], pos, 31); pos++;
		patch[pos] = clamp(patch[pos], pos, 99); pos++;
		patch[pos] = clamp(patch[pos], pos, 14); pos++;
	}
	for(int k=0;k<8;k++) {
		patch[pos] = clamp(patch[pos], pos, 99); pos++;
	}
	patch[pos] = clamp(patch[pos], pos, 31); pos++;
	patch[pos] = clamp(patch[pos], pos, 7); pos++;
	patch[pos] = clamp(patch[pos], pos, 1); pos++;
	patch[pos] = clamp(patch[pos], pos, 99); pos++;
	patch[pos] = clamp(patch[pos], pos, 99); pos++;
	patch[pos] = clamp(patch[pos], pos, 99); pos++;
	patch[pos] = clamp(patch[pos], pos, 99); pos++;

	patch[pos] = clamp(patch[pos], pos, 1); pos++;
	patch[pos] = clamp(patch[pos], pos, 5); pos++;
	patch[pos] = clamp(patch[pos], pos, 7); pos++;
	patch[pos] = clamp(patch[pos], pos, 48); pos++;

	for(int k=0;k<10;k++) {
		patch[pos] = clamp(patch[pos], pos, 126); pos++;
	}

}