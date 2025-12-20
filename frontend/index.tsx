export enum CommentType {
  NORMAL = '정상',
  SPAM = '스팸',
  PROFANITY = '욕설',
  SLANDER = '비방'
}

export enum CommentStatus {
  ACTIVE = 'ACTIVE',
  BLOCKED = 'BLOCKED'
}

export interface Comment {
  id: string;
  author: string;
  authorId: string;
  text: string;
  timestamp: string;
  type: CommentType;
  status: CommentStatus;
  reportCount: number;
  language?: string;
  languageCode?: string;
}

export interface TrollHistoryItem {
  timestamp: string;
  text: string;
  videoTitle: string;
  type: CommentType;
}

export interface BlacklistEntry {
  authorId: string;
  authorName: string;
  reason: string;
  addedAt: string;
  profile?: {
    riskLevel: 'HIGH' | 'CRITICAL' | 'MODERATE';
    activeHours: string;
    behaviorSummary: string;
    history: TrollHistoryItem[];
  };
}