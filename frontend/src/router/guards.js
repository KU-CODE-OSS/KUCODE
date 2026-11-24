import { useAuthStore } from '../stores/auth'

export const protectedPath = path => ['/board', '/ranking', '/eprofile', '/info', '/statistics', '/qna']
  .some(prefix => path === prefix || path.startsWith(`${prefix}/`))

export const adminPath = path => ['/info', '/statistics']
  .some(prefix => path === prefix || path.startsWith(`${prefix}/`)) ||
  ['/board/event/create', '/board/materials/create'].includes(path)

export const authGuard = async (to, from, next) => {
  const store = useAuthStore()
  await store.checkSession()
  if (!store.isAuthenticated) return next('/login')
  if (adminPath(to.path) && !store.isAdmin) return next('/board')
  next()
}

export const guestGuard = async (to, from, next) => {
  const store = useAuthStore()
  await store.checkSession()
  next(store.isAuthenticated ? '/board' : undefined)
}
