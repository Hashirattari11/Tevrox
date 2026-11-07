import { Button, Text, View } from "react-native";
import { router } from "expo-router";
import { tokens } from "@/services/tokenStorage";
export default function Dashboard(){return <View style={{padding:24,gap:12}}><Text style={{fontSize:28}}>Tevrox dashboard</Text><Text>Your profile is connected.</Text><Button title="Log out" onPress={()=>tokens.clear().then(()=>router.replace("/login"))}/></View>}
