// File: /Users/rick/CaseProject/frontend/src/components/auth/Profile.js
import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <div>Loading user profile...</div>;
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="user-profile">
      <div className="profile-image">
        <img src={user.picture} alt={user.name} />
      </div>
      <div className="profile-info">
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    </div>
  );
};

export default Profile;
