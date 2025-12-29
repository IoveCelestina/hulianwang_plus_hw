import request from '@/utils/request'

export type AddressOut = {
  id: number
  contact_name: string
  phone: string
  address_line: string
  is_default: boolean
}

export type AddressIn = {
  contact_name: string
  phone: string
  address_line: string
  is_default?: boolean
}

export const listAddresses = () => request.get('/addresses') as Promise<AddressOut[]>
export const createAddress = (payload: AddressIn) => request.post('/addresses', payload) as Promise<AddressOut>
export const setDefaultAddress = (id: number) => request.post(`/addresses/${id}/set-default`)
