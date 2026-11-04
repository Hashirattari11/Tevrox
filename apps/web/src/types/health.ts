export type Health = { status: string; service: string; version: string; database: "connected" | "unreachable"; mongodb: "connected" | "unreachable" };
