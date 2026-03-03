<template>
  <div id="app">
    <MainLayout v-if="isLoggedIn" />
    <router-view v-else />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/MainLayout.vue'

export default {
  name: 'App',
  components: {
    MainLayout
  },
  setup() {
    const route = useRoute()
    const isLoggedIn = computed(() => {
      const token = localStorage.getItem('token')
      const publicRoutes = ['/login', '/register']
      return token && !publicRoutes.includes(route.path)
    })

    return {
      isLoggedIn
    }
  }
}
</script>
