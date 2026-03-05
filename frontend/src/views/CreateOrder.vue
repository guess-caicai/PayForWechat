<template>
  <div class="create-order page-shell">
    <el-card>
      <template #header>
        <div class="card-header page-card-header">
          <span>💰 创建支付订单</span>
        </div>
      </template>

      <el-form
        :model="orderForm"
        :rules="rules"
        ref="orderFormRef"
        label-width="120px"
        class="order-form"
      >
        <el-form-item label="开发者订单号" prop="developer_order_no">
          <el-input
            v-model="orderForm.developer_order_no"
            placeholder="请输入开发者订单号（唯一标识）"
          />
        </el-form-item>

        <el-form-item label="订单金额" prop="amount">
          <el-input-number
            v-model="orderForm.amount"
            :min="0.01"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          >
            <template #suffix>¥</template>
          </el-input-number>
        </el-form-item>

        <el-form-item label="回调URL" prop="notify_url">
          <el-input
            v-model="orderForm.notify_url"
            placeholder="请输入支付成功后的回调地址"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            生成支付二维码
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 支付二维码预览 -->
      <div v-if="qrCode" class="qr-preview">
        <h3>支付二维码</h3>
        <div class="qr-container">
          <img :src="qrCode" alt="支付二维码" />
        </div>
        <div class="qr-info">
          <p><strong>平台订单号：</strong>{{ platformOrderNo }}</p>
          <p><strong>金额：</strong>¥{{ orderForm.amount }}</p>
          <p><strong>状态：</strong><el-tag type="warning">待支付</el-tag></p>
          <el-button type="primary" @click="handleMockPay">模拟支付</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createOrder } from '@/api'

export default {
  name: 'CreateOrder',
  setup() {
    const orderFormRef = ref(null)
    const loading = ref(false)
    const qrCode = ref('')
    const platformOrderNo = ref('')
    const payUrl = ref('')

    const orderForm = reactive({
      developer_order_no: '',
      amount: 1.00,
      notify_url: 'http://localhost:8000/callback'
    })

    const rules = {
      developer_order_no: [
        { required: true, message: '请输入开发者订单号', trigger: 'blur' }
      ],
      amount: [
        { required: true, message: '请输入订单金额', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
      ],
      notify_url: [
        { required: true, message: '请输入回调URL', trigger: 'blur' }
      ]
    }

    const handleSubmit = async () => {
      await orderFormRef.value.validate()

      loading.value = true
      try {
        const res = await createOrder(orderForm)
        qrCode.value = res.qr_code
        platformOrderNo.value = res.platform_order_no
        payUrl.value = res.pay_url

        ElMessage.success('订单创建成功！')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '创建订单失败')
      } finally {
        loading.value = false
      }
    }

    const handleReset = () => {
      orderFormRef.value.resetFields()
      qrCode.value = ''
      platformOrderNo.value = ''
      payUrl.value = ''
    }

    const handleMockPay = () => {
      if (!payUrl.value) return
      window.open(payUrl.value, '_blank')
    }

    return {
      orderForm,
      rules,
      orderFormRef,
      loading,
      qrCode,
      platformOrderNo,
      payUrl,
      handleSubmit,
      handleReset,
      handleMockPay
    }
  }
}
</script>

<style scoped>
.create-order {
  max-width: 800px;
  margin: 0 auto;
  padding: 0;
}

.order-form {
  padding-right: 20px;
}

.qr-preview {
  margin-top: 30px;
  padding: 20px;
  background-color: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.qr-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.qr-container img {
  width: 250px;
  height: 250px;
  border: 1px solid #ddd;
  padding: 10px;
  background-color: white;
}

.qr-info {
  text-align: center;
  margin-top: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

@media (max-width: 900px) {
  .order-form {
    padding-right: 0;
  }
}
</style>
