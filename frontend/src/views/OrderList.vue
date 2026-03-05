<template>
  <div class="order-list page-shell">
    <el-card>
      <template #header>
        <div class="card-header page-card-header">
          <span>📋 全部订单</span>
          <el-button type="primary" @click="$router.push('/pay/create')">
            <el-icon><Plus /></el-icon>
            创建订单
          </el-button>
        </div>
      </template>

      <el-form :inline="true" class="search-form">
        <el-form-item label="订单状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="待支付" :value="0" />
            <el-option label="已支付" :value="1" />
            <el-option label="已取消" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="platform_order_no" label="平台订单号" width="200" />
        <el-table-column prop="developer_order_no" label="开发者订单号" width="180" />
        <el-table-column prop="amount" label="订单金额" width="100">
          <template #default="{ row }">
            ¥{{ row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="platform_fee" label="手续费" width="100">
          <template #default="{ row }">
            ¥{{ row.platform_fee }}
          </template>
        </el-table-column>
        <el-table-column prop="developer_income" label="开发者收入" width="100">
          <template #default="{ row }">
            ¥{{ row.developer_income }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_time" label="支付时间" width="180">
          <template #default="{ row }">
            {{ row.pay_time ? formatTime(row.pay_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchOrders"
        @size-change="fetchOrders"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { getOrders } from '@/api'

export default {
  name: 'OrderList',
  setup() {
    const loading = ref(false)
    const orders = ref([])

    const searchForm = reactive({
      status: null
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

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
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }

    const fetchOrders = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.page_size
        }
        if (searchForm.status !== null && searchForm.status !== undefined) {
          params.status = searchForm.status
        }

        const res = await getOrders(params)
        orders.value = res.data
        pagination.total = res.total
      } catch (error) {
        console.error('获取订单失败', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      pagination.page = 1
      fetchOrders()
    }

    const handleReset = () => {
      searchForm.status = null
      pagination.page = 1
      fetchOrders()
    }

    onMounted(() => {
      fetchOrders()
    })

    return {
      loading,
      orders,
      searchForm,
      pagination,
      getStatusText,
      getStatusType,
      formatTime,
      fetchOrders,
      handleSearch,
      handleReset
    }
  }
}
</script>

<style scoped>
.order-list {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
  padding: 10px 12px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

@media (max-width: 900px) {
  .card-header {
    gap: 10px;
    flex-wrap: wrap;
  }
}
</style>
