import { useState, useEffect } from 'react';

interface ResponsiveState {
  isMobile: boolean;   // < 768px
  isTablet: boolean;   // 768-1024px
  isDesktop: boolean;  // > 1024px
  isUltrawide: boolean; // > 1920px
}

const MOBILE_QUERY = '(max-width: 767px)';
const TABLET_QUERY = '(min-width: 768px) and (max-width: 1024px)';
const ULTRAWIDE_QUERY = '(min-width: 1921px)';

export function useResponsive(): ResponsiveState {
  const [state, setState] = useState<ResponsiveState>(() => ({
    isMobile: window.matchMedia(MOBILE_QUERY).matches,
    isTablet: window.matchMedia(TABLET_QUERY).matches,
    isDesktop: !window.matchMedia('(max-width: 1024px)').matches,
    isUltrawide: window.matchMedia(ULTRAWIDE_QUERY).matches,
  }));

  useEffect(() => {
    const mobileMq = window.matchMedia(MOBILE_QUERY);
    const tabletMq = window.matchMedia(TABLET_QUERY);
    const ultrawideMq = window.matchMedia(ULTRAWIDE_QUERY);

    const update = () => {
      setState({
        isMobile: mobileMq.matches,
        isTablet: tabletMq.matches,
        isDesktop: !mobileMq.matches && !tabletMq.matches,
        isUltrawide: ultrawideMq.matches,
      });
    };

    mobileMq.addEventListener('change', update);
    tabletMq.addEventListener('change', update);
    ultrawideMq.addEventListener('change', update);
    return () => {
      mobileMq.removeEventListener('change', update);
      tabletMq.removeEventListener('change', update);
      ultrawideMq.removeEventListener('change', update);
    };
  }, []);

  return state;
}
