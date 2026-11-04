import { useState } from "react";
import { Button, TextInput, View, Text } from "react-native";
import { router } from "expo-router";
import { auth } from "@/src/services/api";
export default function Login(){const [email,setEmail]=useState("");const [password,setPassword]=useState("");const [error,setError]=useState("");return <View style={{padding:24,gap:12}}><Text style={{fontSize:28}}>Log in</Text><TextInput placeholder="Email" autoCapitalize="none" value={email} onChangeText={setEmail}/><TextInput placeholder="Password" secureTextEntry value={password} onChangeText={setPassword}/>{error?<Text>{error}</Text>:null}<Button title="Log in" onPress={()=>auth("login",{email,password}).then(()=>router.replace("/dashboard")).catch(e=>setError(e.message))}/><Button title="Create account" onPress={()=>router.push("/signup")}/></View>}
