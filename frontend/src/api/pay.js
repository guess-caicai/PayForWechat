import request from '@/utils/request'

export function createOrder(data) {
  return request({
    url: '/pay/create',
    method: 'post',
    data
  })
}

export function getOrders(params) {
  return request({
    url: '/pay',
    method: 'get',
    params
  })
}

export function getSuccessOrders(params) {
  return request({
    url: '/pay/success',
    method: 'get',
    params
  })
}
