"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  ShieldCheck,
  User,
} from "lucide-react";

import { login, saveAccessToken } from "../../lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError("");

    if (!username.trim()) {
      setError("Please enter your username.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    try {
      setLoading(true);

      const result = await login(
        username.trim(),
        password,
      );

      saveAccessToken(result.access_token);

      window.location.href = "/";
    } catch (err) {
      console.error("Login error:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to login.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#07090d] text-white">
      <div className="flex min-h-screen items-center justify-center px-5 py-10">
        <div className="w-full max-w-md">

          {/* Logo */}

          <div className="mb-8 flex flex-col items-center">
            <div className="relative h-20 w-20 overflow-hidden rounded-2xl border border-white/10 bg-black shadow-2xl">
              <Image
                src="/aladdin-logo.png"
                alt="Aladdin"
                fill
                priority
                sizes="80px"
                className="object-cover"
              />
            </div>

            <h1 className="mt-5 text-xl font-semibold tracking-[0.25em]">
              ALADDIN
            </h1>

            <p className="mt-2 text-[10px] uppercase tracking-[0.2em] text-gray-600">
              Forex Intelligence
            </p>
          </div>

          {/* Login Card */}

          <div className="rounded-2xl border border-white/10 bg-[#0b0f15] p-6 shadow-2xl sm:p-8">

            <div className="mb-7">
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-400">
                Secure Access
              </p>

              <h2 className="mt-2 text-2xl font-semibold">
                Welcome back
              </h2>

              <p className="mt-2 text-sm leading-6 text-gray-500">
                Sign in to access your Aladdin trading
                workspace.
              </p>
            </div>

            {/* Error */}

            {error && (
              <div className="mb-5 rounded-xl border border-red-400/20 bg-red-400/5 px-4 py-3">
                <p className="text-sm text-red-400">
                  {error}
                </p>
              </div>
            )}

            <form
              onSubmit={handleSubmit}
              className="space-y-5"
            >

              {/* Username */}

              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-xs font-medium text-gray-400"
                >
                  Username
                </label>

                <div className="relative">
                  <User
                    size={17}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600"
                  />

                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(event) =>
                      setUsername(event.target.value)
                    }
                    placeholder="Enter your username"
                    autoComplete="username"
                    className="w-full rounded-xl border border-white/10 bg-[#07090d] py-3 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/40 focus:ring-1 focus:ring-emerald-400/20"
                  />
                </div>
              </div>

              {/* Password */}

              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-xs font-medium text-gray-400"
                >
                  Password
                </label>

                <div className="relative">
                  <LockKeyhole
                    size={17}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600"
                  />

                  <input
                    id="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    className="w-full rounded-xl border border-white/10 bg-[#07090d] py-3 pl-10 pr-11 text-sm text-white outline-none transition placeholder:text-gray-700 focus:border-emerald-400/40 focus:ring-1 focus:ring-emerald-400/20"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        (current) => !current,
                      )
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 transition hover:text-gray-300"
                  >
                    {showPassword ? (
                      <EyeOff size={17} />
                    ) : (
                      <Eye size={17} />
                    )}
                  </button>
                </div>
              </div>

              {/* Login */}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 py-3 text-sm font-semibold text-[#06100c] transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#06100c]/30 border-t-[#06100c]" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign in
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            {/* Security */}

            <div className="mt-6 flex items-center gap-3 rounded-xl border border-emerald-400/10 bg-emerald-400/5 p-3">
              <ShieldCheck
                size={18}
                className="shrink-0 text-emerald-400"
              />

              <p className="text-[10px] leading-5 text-gray-500">
                Your session is protected using
                JWT-based authentication.
              </p>
            </div>
          </div>

          <p className="mt-6 text-center text-[10px] text-gray-700">
            Aladdin AI · Forex Trading Assistant
          </p>
        </div>
      </div>
    </main>
  );
}