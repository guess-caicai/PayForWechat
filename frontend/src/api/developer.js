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
    url: '/developer/profile',
    method: 'get'
  })
}

export function getApiKeys() {
  return request({
    url: '/developer/api-keys',
    method: 'get'
  })
}

export function rotateApiKeys(password) {
  return request({
    url: '/developer/api-keys/rotate',
    method: 'post',
    data: { password }
  })
}

export function bindWechatOpenid(wechat_openid) {
  return request({
    url: '/developer/wechat/bind',
    method: 'post',
    data: { wechat_openid }
  })
}
