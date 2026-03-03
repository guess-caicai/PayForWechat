import request from '@/utils/request'

export function applyWithdraw(data) {
  return request({
    url: '/withdraw/apply',
    method: 'post',
    data
  })
}

export function getWithdraws(params) {
  return request({
    url: '/withdraw',
    method: 'get',
    params
  })
}

export function approveWithdraw(id) {
  return request({
    url: '/admin/withdraw/approve',
    method: 'post',
    params: { withdraw_id: id }
  })
}

export function rejectWithdraw(id) {
  return request({
    url: '/admin/withdraw/reject',
    method: 'post',
    params: { withdraw_id: id }
  })
}
