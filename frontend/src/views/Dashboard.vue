<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 今日收入 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon income-icon">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">今日收入</div>
            <div class="stat-value">¥0.00</div>
          </div>
        </el-card>
      </el-col>

      <!-- 总收入 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总收入</div>
            <div class="stat-value">¥{{ wallet.total_income || 0 }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- 可用余额 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon balance-icon">
            <el-icon><BankCard /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">可用余额</div>
            <div class="stat-value">¥{{ wallet.balance || 0 }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- 总提现 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon withdraw-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总提现</div>
            <div class="stat-value">¥{{ wallet.total_withdraw || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/pay/create')">
              <el-icon><Plus /></el-icon>
              创建支付订单
            </el-button>
            <el-button type="success" @click="$router.push('/wallet')">
              <el-icon><Wallet /></el-icon>
              钱包管理
            </el-button>
            <el-button type="warning" @click="$router.push('/withdraw')">
              <el-icon><Upload /></el-icon>
              申请提现
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近订单</span>
              <el-button text @click="$router.push('/orders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="platform_order_no" label="平台订单号" width="200" />
            <el-table-column prop="developer_order_no" label="开发者订单号" width="150" />
            <el-table-column prop="amount" label="金额" width="100">
              <template #default="{ row }">
                ¥{{ row.amount }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>开发者信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="邮箱">{{ userInfo.email }}</el-descriptions-item>
            <el-descriptions-item label="Pay Key">{{ userInfo.pay_key }}</el-descriptions-item>
            <el-descriptions-item label="账号状态">
              <el-tag type="success" v-if="userInfo.status === 1">正常</el-tag>
              <el-tag type="danger" v-else>禁用</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formatTime(userInfo.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, getWallet, getOrders } from '@/api'

export default {
  name: 'Dashboard',
  setup() {
    const wallet = reactive({
      balance: 0,
      frozen_balance: 0,
      total_income: 0,
      total_withdraw: 0
    })

    const userInfo = reactive({
      email: '',
      pay_key: '',
      status: 1,
      created_at: ''
    })

    const recentOrders = ref([])

    const getStatusText = (status) => {
      const map = { 0: '待支付', 1: '已支付', 2: '已取消' }
      return map[status] || '未知'
    }

    const getStatusType = (status) => {
      const map = { 0: 'warning', 1: 'success', 2: 'danger' }
      return map[status] || ''
    }

    const formatTime = (time) => {
      if (!time) return ''
      return new Date(time).toLocaleString('zh-CN')
    }

    const fetchWallet = async () => {
      try {
        const res = await getWallet()
        Object.assign(wallet, res)
      } catch (error) {
        console.error('获取钱包信息失败', error)
      }
    }

    const fetchProfile = async () => {
      try {
        const res = await getProfile()
        Object.assign(userInfo, res)
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    }

    const fetchOrders = async () => {
      try {
        const res = await getOrders({ page: 1, page_size: 10 })
        recentOrders.value = res.data
      } catch (error) {
        console.error('获取订单失败', error)
      }
    }

    onMounted(() => {
      fetchWallet()
      fetchProfile()
      fetchOrders()
    })

    return {
      wallet,
      userInfo,
      recentOrders,
      getStatusText,
      getStatusType,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 20px;
  font-size: 60px;
  opacity: 0.2;
}

.income-icon { color: #409eff; }
.total-icon { color: #67c23a; }
.balance-icon { color: #e6a23c; }
.withdraw-icon { color: #f56c6c; }

.stat-info {
  padding: 20px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 30px;
  font-weight: bold;
  color: #303133;
}

.quick-actions {
  display: flex;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
