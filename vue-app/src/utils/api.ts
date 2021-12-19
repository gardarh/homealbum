const BASE_URL = '/api/v1'
const API_RESOURCE_USER = `auth/user/`
const API_RESOURCE_LOGIN = `auth/login/`

import {
    getCookie
} from './utils'

type HttpMethod = 'POST'|'PUT'|'GET'|'PATCH'|'DELETE'
function apiFetch<T>(
    apiResource: string,
    method: HttpMethod = 'GET',
    payload?: any
): Promise<T> {
    const init: RequestInit = {
        method: method,
    }
    const csrfToken = getCookie('csrftoken');
    if(payload !== undefined) {
        init.body = JSON.stringify(payload)
        init.headers = {
            'Content-Type': 'application/json'
        }
        if(csrfToken !== null) {
            init.headers['X-CSRFToken'] = csrfToken
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

export const loginPost = function(parms: LoginForm): Promise<Response> {
    return fetch(`${BASE_URL}/${API_RESOURCE_LOGIN}`, {
        method: 'POST',
        body: JSON.stringify(parms),
        headers: {
            'Content-Type': 'application/json'
        },
    })
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

export const albumItemUpdateTags = function(
    albumId: number, albumItemId: number, tags: string[]
): Promise<AlbumItem> {
    const payLoad: MediaItemTagUpdate = {tags: tags}
    return apiFetch<AlbumItem>(
        `albums/${albumId}/album-items/${albumItemId}/apply-tags/`,
        'POST',
        payLoad
    )
}
