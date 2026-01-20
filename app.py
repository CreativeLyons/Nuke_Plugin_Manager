"""
Nuke Plugin Manager GUI Application.

PySide6-based external application for managing Nuke plugin configuration.
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import load_config, save_config
from plugin_state import build_plugin_state, set_plugin_enabled, set_vanilla, set_plugins_root


class PluginManagerWindow(QMainWindow):
    """Main window for the Plugin Manager application."""

    def __init__(self, config_path: str):
        """
        Initialize the Plugin Manager window.

        Args:
            config_path: Path to the configuration JSON file
        """
        super().__init__()
        self.config_path = config_path
        self.config = load_config(config_path)
        self.plugin_checkboxes = {}  # Map plugin name to checkbox widget

        self.setWindowTitle("Nuke Plugin Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Plugins folder section
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Plugins folder:")
        self.plugins_root_edit = QLineEdit()
        self.plugins_root_edit.setText(self.config.get("plugins_root", ""))
        self.plugins_root_edit.textChanged.connect(self._on_plugins_root_changed)
        browse_button = QPushButton("Browse…")
        browse_button.clicked.connect(self._on_browse_clicked)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.plugins_root_edit)
        folder_layout.addWidget(browse_button)
        main_layout.addLayout(folder_layout)

        # Warning area
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: #d32f2f; padding: 8px;")
        warning_font = QFont()
        warning_font.setBold(True)
        self.warning_label.setFont(warning_font)
        self.warning_label.hide()
        main_layout.addWidget(self.warning_label)

        # Vanilla Nuke checkbox
        self.vanilla_checkbox = QCheckBox("Vanilla Nuke")
        vanilla_font = QFont()
        vanilla_font.setPointSize(vanilla_font.pointSize() + 2)
        self.vanilla_checkbox.setFont(vanilla_font)
        self.vanilla_checkbox.setChecked(self.config.get("vanilla", False))
        self.vanilla_checkbox.toggled.connect(self._on_vanilla_changed)
        main_layout.addWidget(self.vanilla_checkbox)

        # Plugin list scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.plugin_list_widget = QWidget()
        self.plugin_list_layout = QVBoxLayout(self.plugin_list_widget)
        self.plugin_list_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.plugin_list_widget)
        main_layout.addWidget(self.scroll_area)
        # Update enabled state after widget is assigned to scroll area
        self.update_enabled_state()

        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #2e7d32; padding: 4px;")
        main_layout.addWidget(self.status_label)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self._on_done_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.done_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        # Initial update
        self._update_plugin_list()
        self._update_warning()
        self._update_button_states()
        self.update_enabled_state()

    def _on_plugins_root_changed(self, text: str):
        """Handle plugins root path change."""
        self.config = set_plugins_root(self.config, text)
        self.status_label.setText("")  # Clear status on change
        self._update_plugin_list()
        self._update_warning()
        self._update_button_states()

    def _on_browse_clicked(self):
        """Handle browse button click."""
        from PySide6.QtWidgets import QFileDialog

        current_path = self.plugins_root_edit.text()
        if current_path:
            start_dir = str(Path(current_path).parent)
        else:
            start_dir = str(Path.cwd())

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Plugins Folder",
            start_dir
        )

        if folder:
            self.plugins_root_edit.setText(folder)

    def _on_vanilla_changed(self, checked: bool):
        """Handle vanilla checkbox change."""
        self.config = set_vanilla(self.config, checked)
        self.status_label.setText("")  # Clear status on change
        self.update_enabled_state()

    def _on_plugin_checkbox_changed(self, plugin_name: str, state: int):
        """Handle plugin checkbox change."""
        enabled = state == Qt.Checked
        self.config = set_plugin_enabled(self.config, plugin_name, enabled)
        self.status_label.setText("")  # Clear status on change

    def _on_save_clicked(self):
        """Handle save button click."""
        if self._is_plugins_root_valid():
            success = save_config(self.config_path, self.config)
            if success:
                self.status_label.setText("✅ Config saved")
            else:
                QMessageBox.warning(self, "Save Failed", "Failed to save configuration.")

    def _on_done_clicked(self):
        """Handle done button click."""
        if self._is_plugins_root_valid():
            success = save_config(self.config_path, self.config)
            if success:
                self.status_label.setText("✅ Config saved")
                self.close()
            else:
                QMessageBox.warning(self, "Save Failed", "Failed to save configuration.")

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        # Reload config from disk to discard changes
        self.config = load_config(self.config_path)
        self.close()

    def _is_plugins_root_valid(self) -> bool:
        """Check if plugins_root is valid."""
        plugins_root = self.config.get("plugins_root", "")
        if not plugins_root:
            return False
        path = Path(plugins_root)
        return path.exists() and path.is_dir()

    def _update_warning(self):
        """Update the warning label based on plugins_root validity."""
        if self._is_plugins_root_valid():
            self.warning_label.hide()
        else:
            self.warning_label.setText(
                "<b>Plugins folder not found</b><br>"
                "No plugins will be loaded until a valid plugins folder is selected.<br>"
                "Please choose a plugins folder to continue."
            )
            self.warning_label.show()

    def _update_plugin_list(self):
        """Update the plugin list from current config."""
        # Clear existing checkboxes
        for checkbox in self.plugin_checkboxes.values():
            checkbox.setParent(None)
            checkbox.deleteLater()
        self.plugin_checkboxes.clear()

        # Build plugin state
        state = build_plugin_state(self.config)
        plugins = state.get("plugins", [])

        # Create checkboxes for each plugin
        for plugin in plugins:
            plugin_name = plugin.get("name", "")
            enabled = plugin.get("enabled", False)
            underscore_disabled = plugin.get("underscore_disabled", False)

            checkbox = QCheckBox(plugin_name)
            checkbox.setChecked(enabled)
            checkbox.setEnabled(not underscore_disabled)

            # If underscore-disabled, ensure it's unchecked
            if underscore_disabled:
                checkbox.setChecked(False)

            checkbox.stateChanged.connect(
                lambda state, name=plugin_name: self._on_plugin_checkbox_changed(name, state)
            )

            self.plugin_checkboxes[plugin_name] = checkbox
            self.plugin_list_layout.addWidget(checkbox)

        # Add stretch at the end
        self.plugin_list_layout.addStretch()

        # Update enabled state based on vanilla
        self.update_enabled_state()

    def update_enabled_state(self):
        """Update enabled state of plugin list container based on vanilla mode."""
        vanilla = self.config.get("vanilla", False)
        # Disable the scroll area's content widget that holds the plugin checkboxes
        widget = self.scroll_area.widget()
        if widget:
            widget.setEnabled(not vanilla)

    def _update_button_states(self):
        """Update button enabled states."""
        is_valid = self._is_plugins_root_valid()
        self.save_button.setEnabled(is_valid)
        self.done_button.setEnabled(is_valid)
        # Cancel is always enabled


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Nuke Plugin Manager")
    parser.add_argument(
        "--config",
        type=str,
        default="./plugin_manager.json",
        help="Path to configuration JSON file (default: ./plugin_manager.json)"
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = PluginManagerWindow(args.config)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
