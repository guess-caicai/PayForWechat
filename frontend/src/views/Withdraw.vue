<template>
  <div class="withdraw page-shell">
    <el-row :gutter="20">
      <!-- 申请提现 -->
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>
            <div class="card-header page-card-header">
              <span>💰 申请提现</span>
            </div>
          </template>

          <el-form
            :model="withdrawForm"
            :rules="rules"
            ref="withdrawFormRef"
            label-width="100px"
          >
            <el-form-item label="可用余额">
              <div class="balance-info">
                <el-tag type="success">¥{{ wallet.balance || 0 }}</el-tag>
              </div>
            </el-form-item>

            <el-form-item label="提现金额" prop="amount">
              <el-input-number
                v-model="withdrawForm.amount"
                :min="1"
                :max="wallet.balance"
                :precision="2"
                :step="1"
                :disabled="withdrawForm.withdraw_all"
                style="width: 100%"
              >
                <template #suffix>¥</template>
              </el-input-number>
              <div class="tip-text">
                最低提现金额：¥1.00
              </div>
            </el-form-item>

            <el-form-item>
              <el-checkbox v-model="withdrawForm.withdraw_all">全额提现（按可用余额）</el-checkbox>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="submitting">
                {{ submitting ? '提交中...' : '提交申请' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 提现记录 -->
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>
            <div class="card-header page-card-header">
              <span>📋 提现记录</span>
            </div>
          </template>

          <el-table :data="withdraws" v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="amount" label="提现金额" width="120">
              <template #default="{ row }">
                ¥{{ row.amount }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="finished_at" label="完成时间" width="180">
              <template #default="{ row }">
                {{ row.finished_at ? formatTime(row.finished_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" v-if="isAdmin">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 0"
                  type="success"
                  size="small"
                  @click="handleApprove(row.id)"
                >
                  通过
                </el-button>
                <el-button
                  v-if="row.status === 0"
                  type="danger"
                  size="small"
                  @click="handleReject(row.id)"
                >
                  拒绝
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="fetchWithdraws"
            @size-change="fetchWithdraws"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWallet, applyWithdraw, getWithdraws } from '@/api'

export default {
  name: 'Withdraw',
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const withdrawFormRef = ref(null)
    const wallet = reactive({
      balance: 0
    })
    const withdraws = ref([])
    const isAdmin = ref(!!localStorage.getItem('admin_key'))

    const withdrawForm = reactive({
      amount: 100,
      withdraw_all: false
    })

    const rules = {
      amount: [
        { required: true, message: '请输入提现金额', trigger: 'blur' },
        { type: 'number', min: 1, message: '最低提现金额为1元', trigger: 'blur' }
      ]
    }

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    const getStatusText = (status) => {
      const map = { 0: '待审核', 1: '已通过', 2: '已拒绝', 3: '已完成' }
      return map[status] || '未知'
    }

    const getStatusType = (status) => {
      const map = { 0: 'warning', 1: 'success', 2: 'danger', 3: 'info' }
      return map[status] || ''
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
        // 如果表单金额超过余额，重置为1
        if (withdrawForm.amount > wallet.balance) {
          withdrawForm.amount = 1
        }
      } catch (error) {
        console.error('获取钱包信息失败', error)
      }
    }

    const fetchWithdraws = async () => {
      loading.value = true
      try {
        const res = await getWithdraws({
          page: pagination.page,
          page_size: pagination.page_size
        })
        withdraws.value = res.data
        pagination.total = res.total
      } catch (error) {
        console.error('获取提现记录失败', error)
      } finally {
        loading.value = false
      }
    }

    const handleSubmit = () => {
      withdrawFormRef.value.validate(async (valid) => {
        if (valid) {
          if (!withdrawForm.withdraw_all && withdrawForm.amount > wallet.balance) {
            ElMessage.error('提现金额不能超过可用余额')
            return
          }

          submitting.value = true
          try {
            const payload = withdrawForm.withdraw_all
              ? { withdraw_all: true }
              : { amount: withdrawForm.amount, withdraw_all: false }
            await applyWithdraw(payload)
            ElMessage.success('提现申请提交成功，等待审核')
            withdrawFormRef.value.resetFields()
            fetchWallet()
            fetchWithdraws()
          } catch (error) {
            ElMessage.error(error.response?.data?.detail || '提现申请失败')
          } finally {
            submitting.value = false
          }
        }
      })
    }

    const handleApprove = (id) => {
      ElMessageBox.confirm('确定要通过该提现申请吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await import('@/api').then(api => api.approveWithdraw(id))
          ElMessage.success('审核通过')
          fetchWithdraws()
        } catch (error) {
          ElMessage.error('操作失败')
        }
      })
    }

    const handleReject = (id) => {
      ElMessageBox.confirm('确定要拒绝该提现申请吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await import('@/api').then(api => api.rejectWithdraw(id))
          ElMessage.success('审核拒绝')
          fetchWithdraws()
        } catch (error) {
          ElMessage.error('操作失败')
        }
      })
    }

    onMounted(() => {
      fetchWallet()
      fetchWithdraws()
    })

    return {
      loading,
      submitting,
      withdrawFormRef,
      wallet,
      withdraws,
      isAdmin,
      withdrawForm,
      rules,
      pagination,
      getStatusText,
      getStatusType,
      formatTime,
      handleSubmit,
      handleApprove,
      handleReject,
      fetchWithdraws
    }
  }
}
</script>

<style scoped>
.withdraw {
  padding: 0;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.balance-info {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.tip-text {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}
</style>
