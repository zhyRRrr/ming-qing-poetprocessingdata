// 诗人信息
export const poetInfo = {
    name: '左錫嘉',
    places: 10,
    description: '唐代著名诗人，游历多地'
}

// 城市坐标点数据
export const pointsData = [
    { name: '常州', value: [119.952301, 31.78278] },
    { name: '北京', value: [116.405285, 39.904989] },
    { name: '江西吉安', value: [114.986373, 27.111699] },
    { name: '江西赣州', value: [114.940278, 25.85097] },
    { name: '安徽安庆', value: [117.063754, 30.543494] },
    { name: '湖北黄冈', value: [114.879365, 30.447711] },
    { name: '巫峡', value: [109.878212, 31.044615] },
    { name: '四川', value: [104.075931, 30.651652] },
    { name: '四川成都', value: [104.065735, 30.659462] },
    { name: '山西定襄', value: [112.957639, 38.477577] }
]

// 路线数据
export const routesData = [
    {
        name: '常州到北京路线',
        color: '#FF5722',
        data: [
            [{ coord: [119.952301, 31.78278] }, { coord: [116.405285, 39.904989] }]
        ]
    },
    {
        name: '北京到江西吉安路线',
        color: '#2196F3',
        data: [
            [{ coord: [116.405285, 39.904989] }, { coord: [114.986373, 27.111699] }]
        ]
    },
    {
        name: '江西赣州到四川路线',
        color: '#4CAF50',
        data: [
            [{ coord: [114.940278, 25.85097] }, { coord: [117.063754, 30.543494] }],
            [{ coord: [117.063754, 30.543494] }, { coord: [114.986373, 27.111699] }],
            [{ coord: [114.986373, 27.111699] }, { coord: [114.879365, 30.447711] }],
            [{ coord: [114.879365, 30.447711] }, { coord: [109.878212, 31.044615] }],
            [{ coord: [109.878212, 31.044615] }, { coord: [104.075931, 30.651652] }]
        ]
    },
    {
        name: '四川成都到山西定襄路线',
        color: '#9C27B0',
        data: [
            [{ coord: [104.065735, 30.659462] }, { coord: [112.957639, 38.477577] }]
        ]
    }
] 