import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

import MainLayout from '../layouts/MainLayout';
import DashboardLayout from '../layouts/DashboardLayout';
import ProtectedRoute from '../components/common/ProtectedRoute';

import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import MyReportsPage from '../pages/MyReportsPage';
import ReportDetailPage from '../pages/ReportDetailPage';
import UploadPage from '../pages/UploadPage';
import ProfilePage from '../pages/ProfilePage';
import NotFoundPage from '../pages/NotFoundPage';

import { ROUTES } from '../config/constants';

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public routes — use Main (landing) layout */}
      <Route element={<MainLayout />}>
        <Route path={ROUTES.HOME} element={<LandingPage />} />
        <Route
          path={ROUTES.LOGIN}
          element={isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <LoginPage />}
        />
        <Route
          path={ROUTES.REGISTER}
          element={isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <RegisterPage />}
        />
      </Route>

      {/* Protected routes — use Dashboard layout */}
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.MY_REPORTS} element={<MyReportsPage />} />
        <Route path={ROUTES.REPORT_DETAIL} element={<ReportDetailPage />} />
        <Route path={ROUTES.UPLOAD} element={<UploadPage />} />
        <Route path={ROUTES.PROFILE} element={<ProfilePage />} />
      </Route>

      {/* 404 */}
      <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;
