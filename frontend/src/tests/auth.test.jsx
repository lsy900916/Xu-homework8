/**
 * 认证相关测试
 */
import { describe, it, expect, beforeEach } from "vitest";
import { saveAuth, getToken, clearAuth, isAuthenticated } from "../utils/auth";

describe("Auth Utils", () => {
  beforeEach(() => {
    // 清理 localStorage
    localStorage.clear();
  });

  it("should save and retrieve token", () => {
    const token = "test_token";
    const expiresIn = 3600;
    const user = { user_id: 1, email: "test@example.com" };

    saveAuth(token, expiresIn, user);

    const retrievedToken = getToken();
    expect(retrievedToken).toBe(token);
  });

  it("should return null for expired token", () => {
    const token = "test_token";
    const expiresIn = -1; // 已过期
    const user = { user_id: 1, email: "test@example.com" };

    saveAuth(token, expiresIn, user);

    const retrievedToken = getToken();
    expect(retrievedToken).toBeNull();
  });

  it("should clear auth data", () => {
    const token = "test_token";
    const expiresIn = 3600;
    const user = { user_id: 1, email: "test@example.com" };

    saveAuth(token, expiresIn, user);
    clearAuth();

    expect(getToken()).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });

  it("should check authentication status", () => {
    expect(isAuthenticated()).toBe(false);

    const token = "test_token";
    const expiresIn = 3600;
    const user = { user_id: 1, email: "test@example.com" };

    saveAuth(token, expiresIn, user);

    expect(isAuthenticated()).toBe(true);
  });
});
