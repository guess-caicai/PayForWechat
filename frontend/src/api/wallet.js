import request from '@/utils/request'

export function getWallet() {
  return request({
    url: '/wallet',
    method: 'get'
  })
}

export function getWalletLogs(params) {
  return request({
    url: '/wallet/logs',
    method: 'get',
    params
  })
}
