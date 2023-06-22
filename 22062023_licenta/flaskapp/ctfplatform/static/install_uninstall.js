$(document).ready(function() {
  $('.install-button').click(function(event) {
    event.preventDefault();

    var releaseName = $(this).attr('id').replace('install_button_', '');
    
    var installButton = $('#install_button_' + releaseName);
    var uninstallButton = $('#uninstall_button_' + releaseName);
    var form = $('#form_' + releaseName);
    var releaseVersion = form.find("input[name='release-version']").val();
    var actionInstall = installButton.val();

    var serverData = {
      "release-name": releaseName,
      "release-version": releaseVersion,
      "action": actionInstall
    };

    $.ajax({
      type: "POST",
      url: form.attr('action'),
      data: JSON.stringify(serverData),
      contentType: "application/json",
      dataType: 'json',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      },
      success: function(response) {
        if (response.success) {
          console.log('installation success');
          installButton.hide();
          uninstallButton.show().data('installed', 'True');
        }
      },
      error: function() {
        alert("An error occurred. Please try again.");
      }
    });
  });

  $('.uninstall-button').click(function(event) {
    event.preventDefault();
    var releaseName = $(this).attr('id').replace('install_button_', '');
    
    var installButton = $('#install_button_' + releaseName);
    var uninstallButton = $('#uninstall_button_' + releaseName);
    var form = $('#form_' + releaseName);
    var releaseVersion = form.find("input[name='release-version']").val();
    var actionUninstall = uninstallButton.val();

    var serverData = {
      "release-name": releaseName,
      "release-version": releaseVersion,
      "action": actionUninstall
    };

    $.ajax({
      type: "POST",
      url: form.attr('action'),
      data: JSON.stringify(serverData),
      contentType: "application/json",
      dataType: 'json',
      beforeSend: function(xhr) {
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      },
      success: function(response) {
        if (response.success) {
          console.log('uninstallation success');
          installButton.show();
          uninstallButton.hide().data('installed', 'False');
        }
      },
      error: function() {
        alert("An error occurred. Please try again.");
      }
    });
  });

  
  $('.uninstall-button').each(function() {
    var installed = $(this).data('installed');
    var releaseName = $(this).attr('id').replace('uninstall_button_', '');
    var installButton = $('#install_button_' + releaseName);

    if (installed === "True") {
      installButton.hide();
      $(this).show();
    } else {
      installButton.show();
      $(this).hide();
    }
  });
});
