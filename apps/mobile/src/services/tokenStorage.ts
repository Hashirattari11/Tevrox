import * as SecureStore from "expo-secure-store";
const access = "tevrox_access"; const refresh = "tevrox_refresh";
export const tokens = { get: async () => ({ access: await SecureStore.getItemAsync(access), refresh: await SecureStore.getItemAsync(refresh) }), set: async (a:string,r:string) => Promise.all([SecureStore.setItemAsync(access,a),SecureStore.setItemAsync(refresh,r)]), clear: async () => Promise.all([SecureStore.deleteItemAsync(access),SecureStore.deleteItemAsync(refresh)]) };
