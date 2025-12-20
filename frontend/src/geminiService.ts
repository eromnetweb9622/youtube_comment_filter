import { CommentType } from './types';

// 임시 Mock 함수들 (나중에 Flask API로 교체)

export const summarizeComments = async (texts: string[]) => {
  // Mock AI 요약
  await new Promise(resolve => setTimeout(resolve, 1000));
  return {
    summary: "전반적으로 긍정적인 반응이 많으나, 일부 악성 댓글이 감지되었습니다.",
    score: 78
  };
};

export const fetchSimulatedComments = async (url: string) => {
  // Mock 댓글 수집 (나중에 Flask API 호출로 교체)
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  return {
    comments: [
      {
        author: '새로운유저',
        text: '이 영상 정말 좋네요!',
        type: CommentType.NORMAL,
        timestamp: new Date().toISOString()
      },
      {
        author: '스팸봇',
        text: '무료 구독자 늘리기! 지금 클릭!',
        type: CommentType.SPAM,
        timestamp: new Date().toISOString()
      }
    ]
  };
};

export const analyzeTrollBehavior = async (authorName: string) => {
  // Mock 트롤 분석
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  return {
    riskLevel: 'HIGH' as const,
    activeHours: '23:00-02:00',
    behaviorSummary: '주로 심야 시간대에 활동하며, 반복적인 비방 댓글 패턴이 감지됨',
    history: [
      {
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        text: '이런 쓰레기 영상은 누가 봐',
        videoTitle: '요리 레시피 모음',
        type: CommentType.SLANDER
      },
      {
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
        text: '구독자 구걸하지 마세요',
        videoTitle: '신제품 리뷰',
        type: CommentType.SLANDER
      }
    ]
  };
};

export const checkBackendStatus = async () => {
  // Mock 백엔드 상태 체크
  return { connected: true };
};