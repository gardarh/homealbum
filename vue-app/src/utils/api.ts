const BASE_URL = '/api/v1'
const API_RESOURCE_USER = `auth/user/`
const API_RESOURCE_LOGIN = `auth/login/`

type HttpMethod = 'POST'|'PUT'|'GET'|'PATCH'|'DELETE'
function apiFetch<T>(
    apiResource: string,
    method: HttpMethod = 'GET',
    payload?: Partial<T>
): Promise<T> {
    const init: RequestInit = {
        method: method,
    }
    if(payload !== undefined) {
        init.body = JSON.stringify(payload)
        init.headers = {
            'Content-Type': 'application/json'
        }
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

export const loginPost = function(parms: LoginForm): Promise<void> {
    return fetch(`${BASE_URL}/${API_RESOURCE_LOGIN}`, {
        method: 'POST',
        body: JSON.stringify(parms),
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(() => void(0))
}

export const albumsListFetch = function(): Promise<AlbumSimple[]> {
    return apiFetch<AlbumSimple[]>('albums/')
}

export const albumFetch = function(albumId: number): Promise<Album> {
    return apiFetch<Album>(`albums/${albumId}/`)
}

export const albumItemFetch = function(albumId: number, albumItemId: number): Promise<AlbumItem> {
    return apiFetch<AlbumItem>(`albums/${albumId}/album-items/${albumItemId}/`)
}
