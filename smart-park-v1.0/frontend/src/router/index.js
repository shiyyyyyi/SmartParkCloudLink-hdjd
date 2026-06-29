import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'Home', component: () => import('../views/Home.vue'), meta: { requiresAuth: true } },
  { path: '/lots/:id', name: 'LotDetail', component: () => import('../views/LotDetail.vue'), meta: { requiresAuth: true } },
  { path: '/reservations', name: 'Reservations', component: () => import('../views/MyReservations.vue'), meta: { requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: () => import('../views/MyOrders.vue'), meta: { requiresAuth: true } },
  { path: '/records', name: 'Records', component: () => import('../views/ParkingRecords.vue'), meta: { requiresAuth: true } },
  { path: '/find-car', name: 'FindCar', component: () => import('../views/FindCar.vue'), meta: { requiresAuth: true } },
  { path: '/mine', name: 'Mine', component: () => import('../views/Mine.vue'), meta: { requiresAuth: true } },
  // Admin - 独立管理后台布局
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, admin: true },
    children: [
      { path: '', name: 'AdminDashboard', component: () => import('../views/admin/Dashboard.vue') },
      { path: 'lots', name: 'AdminLots', component: () => import('../views/admin/LotManagement.vue') },
      { path: 'lots/:id', name: 'AdminLotOverview', component: () => import('../views/admin/LotOverview.vue') },
      { path: 'orders', name: 'AdminOrders', component: () => import('../views/admin/OrderManagement.vue') },
    ]
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) return next('/login')
  const userStr = localStorage.getItem('user')
  if (to.meta.admin && userStr) {
    try {
      const user = JSON.parse(userStr)
      if (user.role !== 'admin') return next('/home')
    } catch { return next('/login') }
  }
  next()
})

export default router
