import { inject, reactive } from "vue"
import { DEFAULT_STATE } from "./consts"

export const stateSymbol = Symbol('state')
export const createState = () => reactive(Object.assign({}, DEFAULT_STATE))
export const useState = () => inject(stateSymbol) as HomeAlbumState