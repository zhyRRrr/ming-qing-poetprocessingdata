export interface Point {
  x: number;
  y: number;
}

export interface EmotionInfo {
  emotion: string;
  poetryQuantity: number;
}
export interface PoetInfo {
  poetId: number;
  birthday: number;
  poemNum: number;
  emotionInfos: Array<EmotionInfo>;
}
export interface PlaceInfo {
  placeName: string;
  poetMaxBirthday: number;
  poetInfos: Array<PoetInfo>;
}

export interface FamilyInfo {
  familyName: string;
  placeMaxBirthday: number;
  placeMaxSpan: number;
  placeInfos: Array<PlaceInfo>;
}
export interface HaveFamilyInfo {
  familyMaxBirthday: number;
  familyMaxSpan: number;
  poemMaxNum: number;
  familyInfos: Array<FamilyInfo>;
}

export interface FamilyPoetsResponse {
  data: {
    data: HaveFamilyInfo;
  }
}

export interface NoFamilyInfo {
  noFamilyMaxBirthday: number;
  maxSpan: number;
  poemMaxNum: number;
  placeInfos: Array<PlaceInfo>;
}
export interface NoFamilyPoetsResponse {
  data: {
    data: NoFamilyInfo;
  }
}

export interface MainInfo {
  startYear: number;
  endYear: number;
}

export interface MainInfoResponse {
  data: {
    data: MainInfo;
  }
}

export interface Flower {
  poetId: number;
  left: number;
  top: number;
  data: EmotionInfo[];
  select: boolean;
  scale: number;
  rotate: number;
}

export interface CycleInfo {
  year: number;
  cycle: string;
}