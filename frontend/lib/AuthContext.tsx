"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { User, SignupInput, LoginInput } from "@/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean; // true only during the initial "am I logged in" check
  signup: (data: SignupInput) => Promise<void>;
  login: (data: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Routes reachable without being logged in. Exported so AppShell can reuse
// the same list to decide whether to render the app's sidebar/chrome --
// one source of truth instead of two arrays that could drift apart.
export const PUBLIC_ROUTES = ["/login", "/signup"];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const checkAuth = useCallback(async () => {
    try {
      const me = await api.auth.me();
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (loading) return;
    const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
    if (!user && !isPublicRoute) {
      router.replace("/login");
    } else if (user && isPublicRoute) {
      router.replace("/dashboard");
    }
  }, [user, loading, pathname, router]);

  async function signup(data: SignupInput) {
    await api.auth.signup(data);
    await checkAuth();
    router.replace("/dashboard");
  }

  async function login(data: LoginInput) {
    await api.auth.login(data);
    await checkAuth();
    router.replace("/dashboard");
  }

  async function logout() {
    await api.auth.logout().catch(() => {});
    setUser(null);
    router.replace("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { ApiError };
