import { useState } from "react";

import { getMe, login } from "features/auth/api";
import { useLoginForm } from "features/auth/useLoginForm";
import { useAuthStore } from "features/auth/authStore";

export function LoginPage() {
  const [requestError, setRequestError] = useState<string | null>(null);
  const form = useLoginForm();
  const authLogin = useAuthStore((state) => state.login);

  const handleSubmit = form.handleSubmit(async (values) => {
    try {
      setRequestError(null);
      const data = await login(values);
      const profile = await getMe(data.access);
      authLogin({
        accessToken: data.access,
        refreshToken: data.refresh,
        fullName: profile.full_name,
        role: profile.role,
      });
    } catch {
      setRequestError("Не удалось выполнить вход. Проверьте доступность backend API.");
    }
  });

  return (
    <section className="login-screen">
      <div className="login-layout">
        <div className="login-hero glass-card">
          <p className="pill">Inspection Workflow</p>
          <h1 className="headline">Обследование без разрозненных таблиц и файловых архивов</h1>
          <p className="muted">
            Система объединяет объект, программу работ, элементы здания, дефекты, измерения, фотофиксацию и итоговое заключение в одну инженерную цепочку.
          </p>
          <div className="kpi-row">
            <div className="kpi-item">
              <div className="muted">Статусы проектов</div>
              <div className="stat-value">6</div>
            </div>
            <div className="kpi-item">
              <div className="muted">Ролевой доступ</div>
              <div className="stat-value">5</div>
            </div>
            <div className="kpi-item">
              <div className="muted">Сквозной отчёт</div>
              <div className="stat-value">1</div>
            </div>
          </div>
        </div>

        <div className="login-card glass-card">
          <p className="pill">Вход в систему</p>
          <h2 className="page-title">Рабочий кабинет инженера</h2>
          <p className="muted">Для demo-сценария можно использовать предзаполненные учетные данные.</p>

          <div className="page-card" style={{ padding: "14px 16px", marginBottom: 16, background: "rgba(255,255,255,0.04)", borderRadius: 16 }}>
            <strong>Demo роли</strong>
            <div className="muted" style={{ marginTop: 8 }}>Admin: `admin@example.com` / `Password123!`</div>
            <div className="muted">Expert: `expert@example.com` / `Password123!`</div>
            <div className="muted">Engineer: `engineer@example.com` / `Password123!`</div>
          </div>

          <form className="form-grid" onSubmit={handleSubmit}>
            <div>
              <label className="label" htmlFor="email">
                Email
              </label>
              <input id="email" className="input" {...form.register("email")} />
              {form.formState.errors.email ? <span className="error-text">{form.formState.errors.email.message}</span> : null}
            </div>

            <div>
              <label className="label" htmlFor="password">
                Пароль
              </label>
              <input id="password" type="password" className="input" {...form.register("password")} />
              {form.formState.errors.password ? <span className="error-text">{form.formState.errors.password.message}</span> : null}
            </div>

            {requestError ? <span className="error-text">{requestError}</span> : null}

            <div className="login-actions">
              <button className="button primary" type="submit">
                Войти
              </button>
              <button className="button" type="button" onClick={() => form.reset()}>
                Очистить
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
