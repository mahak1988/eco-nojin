/**
 * SDG Colors - Official United Nations Colors
 */

export const SDG_COLORS = {
  1: '#E5243B',  2: '#DDA63A',  3: '#4C9F38',  4: '#C5192D',
  5: '#FF3A21',  6: '#26BDE2',  7: '#FCC30B',  8: '#A21942',
  9: '#FD6925',  10: '#DD1367', 11: '#FD9D24', 12: '#BF8B2E',
  13: '#3F7E44', 14: '#0A97D9', 15: '#56C02B', 16: '#00689D',
  17: '#19486A',
} as const;

export const SDG_NAMES = {
  1: 'No Poverty',
  2: 'Zero Hunger',
  3: 'Good Health and Well-being',
  4: 'Quality Education',
  5: 'Gender Equality',
  6: 'Clean Water and Sanitation',
  7: 'Affordable and Clean Energy',
  8: 'Decent Work and Economic Growth',
  9: 'Industry, Innovation and Infrastructure',
  10: 'Reduced Inequalities',
  11: 'Sustainable Cities and Communities',
  12: 'Responsible Consumption and Production',
  13: 'Climate Action',
  14: 'Life Below Water',
  15: 'Life on Land',
  16: 'Peace, Justice and Strong Institutions',
  17: 'Partnerships for the Goals',
} as const;

export type SDGNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17;

export function getSDGColor(goal: SDGNumber): string {
  return SDG_COLORS[goal];
}

export function getSDGName(goal: SDGNumber): string {
  return SDG_NAMES[goal];
}
