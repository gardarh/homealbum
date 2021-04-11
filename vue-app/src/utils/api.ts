const BASE_URL = '/api/v1'
const API_RESOURCE_USER = `auth/user/`

type HttpMethod = 'post'|'put'|'get'|'patch'|'delete'
function apiFetch<T>(
    apiResource: string,
    method: HttpMethod = 'get',
    payload?: Partial<T>
): Promise<T> {
    const init: RequestInit = {
        method: method,
    }
    if(payload !== undefined) {
        init.body = JSON.stringify(payload)
    }
    return fetch(`${BASE_URL}/${apiResource}`, init).then(response => {
        return response.json() as Promise<T>
    })
}

export const systemInfoGet = function(): Promise<SystemInfo> {
    return apiFetch<SystemInfo>('system-info/')
}

export const userGet = function(): Promise<User> {
    return apiFetch<User>(API_RESOURCE_USER)
}