<template>
  <div class="profile page-shell">
    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="page-card-header">
              <span class="page-card-title">Basic Info</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Developer ID">{{ profile.id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Email">{{ profile.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="profile.status === 1 ? 'success' : 'danger'">
                {{ profile.status === 1 ? 'Active' : 'Disabled' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Wechat OpenID">{{ profile.wechat_openid || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Created At">{{ formatTime(profile.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="page-card-header">
              <span class="page-card-title">Stats</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Orders">{{ profile.stats?.order_total ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="Paid Orders">{{ profile.stats?.paid_count ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="Paid Amount">CNY {{ profile.stats?.paid_amount ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="Balance">CNY {{ profile.wallet?.balance ?? 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="page-card-header">
              <span class="page-card-title">API Key Management</span>
              <el-button type="primary" @click="openRotateDialog">Rotate Keys</el-button>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="Receiver OpenID">
              <el-input v-model="wechatOpenid" placeholder="Used for transfer payout" />
              <el-button style="margin-top: 8px" @click="handleBindWechat" :loading="binding">Save OpenID</el-button>
            </el-form-item>

            <el-form-item label="Pay Key">
              <el-input :model-value="apiKeys.pay_key" readonly>
                <template #append>
                  <el-button @click="copyText(apiKeys.pay_key)">Copy</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="Pay Secret">
              <el-input :model-value="maskedSecret" readonly>
                <template #append>
                  <el-button @click="toggleSecret">{{ showSecret ? 'Hide' : 'Show' }}</el-button>
                </template>
              </el-input>
            </el-form-item>

            <div class="tip-text">
              Rotating keys invalidates old credentials immediately. Update your client system right away.
            </div>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="rotateDialogVisible" title="Rotate API Keys" width="420px">
      <el-form>
        <el-form-item label="Password" label-width="90px">
          <el-input v-model="rotatePassword" type="password" show-password placeholder="Current login password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rotateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="rotating" @click="handleRotate">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { bindWechatOpenid, getApiKeys, getProfile, rotateApiKeys } from '@/api'

export default {
  name: 'Profile',
  setup() {
    const profile = reactive({})
    const apiKeys = reactive({
      pay_key: '',
      pay_secret: ''
    })
    const showSecret = ref(false)
    const rotateDialogVisible = ref(false)
    const rotatePassword = ref('')
    const rotating = ref(false)
    const wechatOpenid = ref('')
    const binding = ref(false)

    const maskedSecret = computed(() => {
      if (!apiKeys.pay_secret) return ''
      if (showSecret.value) return apiKeys.pay_secret
      return `${apiKeys.pay_secret.slice(0, 10)}********${apiKeys.pay_secret.slice(-6)}`
    })

    const formatTime = (time) => {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN')
    }

    const fetchProfile = async () => {
      const res = await getProfile()
      Object.assign(profile, res)
      wechatOpenid.value = res.wechat_openid || ''
    }

    const fetchApiKeys = async () => {
      const res = await getApiKeys()
      Object.assign(apiKeys, res)
    }

    const copyText = async (text) => {
      if (!text) return
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('Copied')
      } catch {
        ElMessage.error('Copy failed')
      }
    }

    const toggleSecret = () => {
      showSecret.value = !showSecret.value
    }

    const openRotateDialog = () => {
      rotatePassword.value = ''
      rotateDialogVisible.value = true
    }

    const handleBindWechat = async () => {
      if (!wechatOpenid.value) {
        ElMessage.warning('Please input wechat openid')
        return
      }
      binding.value = true
      try {
        await bindWechatOpenid(wechatOpenid.value.trim())
        profile.wechat_openid = wechatOpenid.value.trim()
        ElMessage.success('OpenID saved')
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || 'Save failed')
      } finally {
        binding.value = false
      }
    }

    const handleRotate = async () => {
      if (!rotatePassword.value) {
        ElMessage.warning('Please input password')
        return
      }
      rotating.value = true
      try {
        const res = await rotateApiKeys(rotatePassword.value)
        Object.assign(apiKeys, res)
        rotateDialogVisible.value = false
        showSecret.value = false
        ElMessage.success('API keys rotated')
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || 'Rotate failed')
      } finally {
        rotating.value = false
      }
    }

    onMounted(async () => {
      try {
        await Promise.all([fetchProfile(), fetchApiKeys()])
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || 'Load profile failed')
      }
    })

    return {
      profile,
      apiKeys,
      showSecret,
      maskedSecret,
      rotateDialogVisible,
      rotatePassword,
      rotating,
      wechatOpenid,
      binding,
      formatTime,
      copyText,
      toggleSecret,
      openRotateDialog,
      handleBindWechat,
      handleRotate
    }
  }
}
</script>

<style scoped>
.profile {
  padding: 0;
}

.tip-text {
  color: #6b7280;
  font-size: 12px;
}
</style>
