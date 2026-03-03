<template>
  <div class="success-orders">
    <el-card>
      <template #header>
        <span>✅ 已支付订单</span>
      </template>

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
        <el-table-column prop="pay_time" label="支付时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.pay_time) }}
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
import { getSuccessOrders } from '@/api'

export default {
  name: 'SuccessOrders',
  setup() {
    const loading = ref(false)
    const orders = ref([])

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN')
    }

    const fetchOrders = async () => {
      loading.value = true
      try {
        const res = await getSuccessOrders({
          page: pagination.page,
          page_size: pagination.page_size
        })
        orders.value = res.data
        pagination.total = res.total
      } catch (error) {
        console.error('获取订单失败', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchOrders()
    })

    return {
      loading,
      orders,
      pagination,
      formatTime,
      fetchOrders
    }
  }
}
</script>

<style scoped>
.success-orders {
  padding: 20px;
}
</style>
