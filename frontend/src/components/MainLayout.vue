<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h2>💰 PayForWechat</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/pay/create">
            <el-icon><Plus /></el-icon>
            <span>创建订单</span>
          </el-menu-item>
          <el-menu-item index="/orders">
            <el-icon><List /></el-icon>
            <span>全部订单</span>
          </el-menu-item>
          <el-menu-item index="/orders/success">
            <el-icon><CircleCheck /></el-icon>
            <span>成功订单</span>
          </el-menu-item>
          <el-menu-item index="/wallet">
            <el-icon><Wallet /></el-icon>
            <span>钱包</span>
          </el-menu-item>
          <el-menu-item index="/withdraw">
            <el-icon><Money /></el-icon>
            <span>提现</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon class="hamburger" @click="toggleSidebar"><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userInfo.email }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getProfile } from '@/api'

export default {
  name: 'MainLayout',
  setup() {
    const router = useRouter()
    const isCollapse = ref(false)
    const userInfo = reactive({
      email: '',
      payKey: ''
    })

    const toggleSidebar = () => {
      isCollapse.value = !isCollapse.value
    }

    const fetchProfile = async () => {
      try {
        const res = await getProfile()
        userInfo.email = res.email
        userInfo.payKey = res.pay_key
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    }

    const handleProfile = () => {
      ElMessage.info('功能开发中...')
    }

    const handleLogout = () => {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        router.push('/login')
      })
    }

    onMounted(() => {
      fetchProfile()
    })

    return {
      isCollapse,
      userInfo,
      toggleSidebar,
      handleProfile,
      handleLogout
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  background-color: #304156;
  height: 100vh;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4b;
}

.logo h2 {
  color: white;
  font-size: 20px;
  margin: 0;
}

.menu {
  border-right: none;
  background-color: #304156;
}

.menu :deep(.el-menu-item) {
  color: #bfcbd9;
}

.menu :deep(.el-menu-item:hover) {
  background-color: #263445 !important;
  color: #409eff !important;
}

.menu :deep(.el-menu-item.is-active) {
  background-color: #263445 !important;
  color: #409eff !important;
}

.el-header {
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.hamburger {
  font-size: 24px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.main-content {
  overflow-y: auto;
}
</style>
