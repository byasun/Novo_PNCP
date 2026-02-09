import React from 'react';
import { SignUp } from '@clerk/clerk-react';

const CreateUserPage = () => (
  <div className="grid">
    <div className="card">
      <SignUp routing="path" path="/users/new" />
    </div>
  </div>
);

export default CreateUserPage;
