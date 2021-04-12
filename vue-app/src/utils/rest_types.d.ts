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