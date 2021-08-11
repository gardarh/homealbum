interface User {
    pk: number
    username: string
    email: string
    first_name: string
    last_name: string
}

interface SystemInfo {
    build_no: number
    version: string
    is_authenticated: boolean
}

interface LoginForm {
    username: string
    password: string
}

interface AlbumSimple {
    id: number
    name: string
    earliest_date: string
    latest_date: string
}

interface Album extends AlbumSimple {
    album_items: AlbumItemSimple[]
}

interface AlbumItemSimple {
    id: number
    album: number
    file_location: string
    media_file: string
}

interface AlbumItem extends AlbumItemSimple {
    media_file_item: MediaFileItem
    raw_url?: string
}


type MediaType = 'photo'|'video'

interface ExifData {
    f_number?: string // e.g. "1/2"
    exposure_time?: string // e.g. "1/100"
    make?: string
    model?: string
    iso?: number,
    date?: string // e.g. "2021-01-10T13:47:24"
}

interface Tag {
    name: string,
}

interface Comment {
    id: number
    comment: string
    media_file: string
}

interface MediaFileItem {
    file_hash: string
    mediatype: MediaType
    file_location: string
    width: number
    height: number
    date_taken: string
    exif_data: ExifData
    tags: Tag[]
    comments: Comment[]
}


type ButtonStyle = 'default'|'link'|'outline'