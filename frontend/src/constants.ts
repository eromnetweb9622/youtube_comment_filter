import { Comment, CommentType, CommentStatus } from './types';

export const MOCK_COMMENTS: Comment[] = [
  {
    id: '1',
    author: '김철수',
    authorId: 'usr_김철수',
    text: '영상 너무 유익해요! 다음편도 기대됩니다.',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    type: CommentType.NORMAL,
    status: CommentStatus.ACTIVE,
    reportCount: 0,
    languageCode: 'ko'
  },
  {
    id: '2',
    author: '재테크왕',
    authorId: 'usr_재테크왕',
    text: '지금 바로 100% 수익 보장! 아래 링크 클릭하세요. http://scam-link.com/win',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    type: CommentType.SPAM,
    status: CommentStatus.ACTIVE,
    reportCount: 3,
    languageCode: 'ko'
  },
  {
    id: '3',
    author: 'Hater_01',
    authorId: 'usr_hater_01',
    text: '실력도 없으면서 왜 유튜브함? 진짜 한심하다 ㅋㅋ 접어라 제발',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    type: CommentType.SLANDER,
    status: CommentStatus.ACTIVE,
    reportCount: 8,
    languageCode: 'ko'
  },
  {
    id: '4',
    author: '욕설금지',
    authorId: 'usr_욕설금지',
    text: '야 이 XXX야, 영상 그따구로 찍지 마라 진짜 기분 나쁘네',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    type: CommentType.PROFANITY,
    status: CommentStatus.ACTIVE,
    reportCount: 12,
    languageCode: 'ko'
  },
  {
    id: '5',
    author: 'Sarah J.',
    authorId: 'usr_sarah_j',
    text: 'Wow, the production quality is getting better every day! Keep it up.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    type: CommentType.NORMAL,
    status: CommentStatus.ACTIVE,
    reportCount: 0,
    languageCode: 'en'
  },
  {
    id: '6',
    author: 'SpamBot99',
    authorId: 'usr_spambot99',
    text: 'Get 5000 subscribers for FREE! No survey! Check my channel info!',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    type: CommentType.SPAM,
    status: CommentStatus.ACTIVE,
    reportCount: 5,
    languageCode: 'en'
  },
  {
    id: '7',
    author: '이영희',
    authorId: 'usr_이영희',
    text: '중간에 나오는 설명이 조금 어려운데 따로 정리된 자료가 있을까요?',
    timestamp: new Date(Date.now() - 1000 * 60 * 150).toISOString(),
    type: CommentType.NORMAL,
    status: CommentStatus.ACTIVE,
    reportCount: 0,
    languageCode: 'ko'
  },
  {
    id: '8',
    author: '비방러A',
    authorId: 'usr_비방러a',
    text: '얼굴 보니까 밥맛 떨어지네... 필터 좀 써라 좀',
    timestamp: new Date(Date.now() - 1000 * 60 * 200).toISOString(),
    type: CommentType.SLANDER,
    status: CommentStatus.ACTIVE,
    reportCount: 15,
    languageCode: 'ko'
  },
  {
    id: '9',
    author: 'GlobalCritic',
    authorId: 'usr_global_critic',
    text: 'This video is total garbage. You should quit YouTube right now.',
    timestamp: new Date(Date.now() - 1000 * 60 * 300).toISOString(),
    type: CommentType.SLANDER,
    status: CommentStatus.ACTIVE,
    reportCount: 4,
    languageCode: 'en'
  }
];