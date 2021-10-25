interface HomeAlbumState {
    user: User|null
    systemInfo: SystemInfo|null
}

type MessageVariant = 'error'|'warning'|'info'|'success'