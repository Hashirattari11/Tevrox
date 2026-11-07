import { useState } from "react";
import { Button, TextInput, View, Text } from "react-native";
import { router } from "expo-router";
import { auth } from "@/services/api";
export default function Signup(){const [full_name,setName]=useState("");const [email,setEmail]=useState("");const [password,setPassword]=useState("");const [error,setError]=useState("");return <View style={{padding:24,gap:12}}><Text style={{fontSize:28}}>Create account</Text><TextInput placeholder="Full name" value={full_name} onChangeText={setName}/><TextInput placeholder="Email" autoCapitalize="none" value={email} onChangeText={setEmail}/><TextInput placeholder="Password (8+ chars)" secureTextEntry value={password} onChangeText={setPassword}/>{error?<Text>{error}</Text>:null}<Button title="Sign up" onPress={()=>auth("signup",{full_name,email,password}).then(()=>router.replace("/onboarding")).catch((e: any)=>setError(e.message))}/></View>}
