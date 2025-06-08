let sidebarOpen = false;

    function toggleSidebar() {
      const sidebar = document.getElementById("sidebar");
      const toggleButton = document.getElementById("toggleButton");

      sidebarOpen = !sidebarOpen;

      sidebar.classList.toggle("sidebar-open");
      sidebar.classList.toggle("sidebar-closed");

      if (sidebarOpen) {
        toggleButton.classList.add("translate-x-72");
        toggleButton.innerHTML = "⮜";
      } else {
        toggleButton.classList.remove("translate-x-72");
        toggleButton.innerHTML = "⮞";
      }
    }