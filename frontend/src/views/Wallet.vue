<template>
  <div class="wallet">
    <el-row :gutter="20">
      <!-- 钱包余额卡片 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>💰 可用余额</span>
            </div>
          </template>
          <div class="balance-display">
            <div class="balance-amount">¥{{ wallet.balance || 0 }}</div>
            <div class="balance-label">可提现金额</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>❄️ 冻结余额</span>
            </div>
          </template>
          <div class="balance-display">
            <div class="balance-amount">¥{{ wallet.frozen_balance || 0 }}</div>
            <div class="balance-label">提现中金额</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📊 统计数据</span>
            </div>
          </template>
          <div class="stats-display">
            <div class="stat-item">
              <div class="stat-label">总收入</div>
              <div class="stat-value">¥{{ wallet.total_income || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">总提现</div>
              <div class="stat-value">¥{{ wallet.total_withdraw || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 钱包流水 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📋 钱包流水</span>
            </div>
          </template>

          <el-table :data="logs" v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="change_type" label="变动类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getChangeType(row.change_type)">
                  {{ row.change_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="变动金额" width="120">
              <template #default="{ row }">
                <span :class="{ 'text-green': row.change_type === '收入', 'text-red': row.change_type !== '收入' }">
                  {{ row.change_type === '收入' ? '+' : '-' }}¥{{ row.amount }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="balance" label="当前余额" width="120">
              <template #default="{ row }">
                ¥{{ row.balance }}
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="fetchLogs"
            @size-change="fetchLogs"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { getWallet, getWalletLogs } from '@/api'

export default {
  name: 'Wallet',
  setup() {
    const loading = ref(false)
    const wallet = reactive({
      balance: 0,
      frozen_balance: 0,
      total_income: 0,
      total_withdraw: 0
    })
    const logs = ref([])

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    const getChangeType = (type) => {
      const map = { '收入': 'success', '提现': 'danger', '冻结': 'warning', '解冻': 'info' }
      return map[type] || ''
    }

    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }

    const fetchWallet = async () => {
      try {
        const res = await getWallet()
        Object.assign(wallet, res)
      } catch (error) {
        console.error('获取钱包信息失败', error)
      }
    }

    const fetchLogs = async () => {
      loading.value = true
      try {
        const res = await getWalletLogs({
          page: pagination.page,
          page_size: pagination.page_size
        })
        logs.value = res.data
        pagination.total = res.total
      } catch (error) {
        console.error('获取钱包流水失败', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchWallet()
      fetchLogs()
    })

    return {
      loading,
      wallet,
      logs,
      pagination,
      getChangeType,
      formatTime,
      fetchLogs
    }
  }
}
</script>

<style scoped>
.wallet {
  padding: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
}

.balance-display {
  text-align: center;
  padding: 30px 0;
}

.balance-amount {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.balance-label {
  color: #909399;
  font-size: 14px;
}

.stats-display {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.text-green {
  color: #67c23a;
}

.text-red {
  color: #f56c6c;
}
</style>
