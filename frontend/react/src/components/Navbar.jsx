import React from "react";

const Navbar = ({ className = "", children, ...props }) => (
  <nav className={`nav ${className}`.trim()} {...props}>
    {children}
  </nav>
);

export default Navbar;
