import { createHashRouter } from '@vkontakte/vk-mini-apps-router';

export const DEFAULT_VIEW_PANELS = {
  HOME: 'home',
  MOVIE_DETAIL: 'movie_detail',
} as const;

export const router = createHashRouter([
  {
    path: '/',
    panel: DEFAULT_VIEW_PANELS.HOME,
    view: 'default_view',
    root: 'default_root',
  },
  {
    path: '/movie/:id',
    panel: DEFAULT_VIEW_PANELS.MOVIE_DETAIL,
    view: 'default_view',
    root: 'default_root',
  },
]);