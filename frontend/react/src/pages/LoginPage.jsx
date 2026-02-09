import React from 'react';
import { SignIn } from '@clerk/clerk-react';

const LoginPage = () => (
  <div className="grid">
    <div className="card">
      <SignIn routing="path" path="/login" />
    </div>
  </div>
);

export default LoginPage;
