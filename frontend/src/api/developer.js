import request from '@/utils/request'

export function register(data) {
  return request({
    url: '/developer/register',
    method: 'post',
    data
  })
}

export function login(data) {
  return request({
    url: '/developer/login',
    method: 'post',
    data
  })
}

export function getProfile() {
  return request({
    url: '/pay/profile',
    method: 'get'
  })
}
